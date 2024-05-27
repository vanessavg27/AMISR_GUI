###################################
#    Engineer: Vanessa Vasquez 2024
#    Jicamarca Radio Observatory
###################################

# ------------------------------------------------------
# ---------------------- main.py -----------------------
# ------------------------------------------------------
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap

from PyQt5 import QtGui
from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)

import numpy
import random

import os
import time
import math
import scipy
import base64
import datetime
from io import BytesIO
import scipy.interpolate
from matplotlib.figure import Figure

import sys
path_m = os.getcwd()
path_m = path_m.split('/')
path_m="/".join(path_m[:-1])+"/Experimentos"
sys.path.append(path_m)
from GUI_genExp_AMISR import *
#sys.path.insert(1,'/home/soporte/app-amisr/realtime_web/volumes/app')
#from app.utils import *
import TimeTools
from patterns import select_pattern
import Misc_Routines
import Astro_Coords
#from utils import gaussfit
from plots import *
from PIL import Image

import matplotlib.pyplot as plt
from matplotlib.backend_bases import MouseButton
from PyQt5.QtCore import QDate, QDateTime
from datetime import datetime
     
class MatplotlibWidget(QMainWindow):
    
    def __init__(self):
        
        QMainWindow.__init__(self)

        loadUi("qt_designer.ui",self)

        self.setWindowTitle("Total Pattern AMISR-14 - GUI")
        self.site = 2
        self.fecha_default()
        ## LISTA DE APUNTES EN TABLA
        self.azimuth_lista   = []
        self.elevation_lista = []
        self.beamhexa = []
        ## LISTA DE APUNTES EN PLOT
        self.xcos = []
        self.ycos = []
        self.row_table = 25
        self.beams = []
        self.update_graph2()
        #Defaults parameters
        self.parameters_experiments_init()
        #Components
        self.pushButton_refresh.clicked.connect(self.reset)
        self.pushButton_plot.clicked.connect(self.draw)
        self.pushButton_del.clicked.connect(self.delete_point)
        self.pushButton_GEN_EXP.clicked.connect(self.set_experiment)
        self.pushButton_addbeam.clicked.connect(self.add_button)
        self.pushButton_close.clicked.connect(self.salida)
        self.pushButton_send_exp.clicked.connect(self.send_exp)
        
        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))
        
        qpixmap = QPixmap("amisr-logo.png")
        self.label_16.setPixmap(qpixmap)
    
    def fecha_default(self):

        now = datetime.now()
        date_default = QDate(now.year,now.month,now.day)
        
        self.fecha_in.setDate(date_default)
        self.fecha = self.fecha_in.date().toPyDate()
        
        fecha_datatime = self.fecha_in.date().toPyDate()
        print(fecha_datatime)
        #return fecha_datatime

    def get_fecha(self):
        self.fecha = self.fecha_in.date().toPyDate()
        
    def draw(self):

        self.MplWidget.canvas.axes.clear()

        if len(self.lineEdit_high.text()) == 0:
            self.high = [100,500]
        else:
            self.high = [ float(i) for i in self.lineEdit_high.text().split(",")]
        self.get_fecha()
        
        cont = 0
        for item in self.tableWidget_lista.selectedItems():
            
            if cont == 0:azi_new = float(item.text())
            elif cont == 2:ele_new = float(item.text())
            cont +=1
        try:
            azimuth = float(self.lineEdit_azimuth.text())
            elevation = float(self.lineEdit_elevation.text())
            print("AZIMUTH INGRESADO:",self.lineEdit_azimuth.text())
            print("ELEVATION INGRESADO:",elevation,type(elevation))
        except:
            try:
                self.update_graph2(azi_new,ele_new,self.high,plot=True)
            except UnboundLocalError:
                print("Select a row from the table or enter parameters in the Azimuth and Elevation boxes")
        else:
            self.update_graph2(azimuth,elevation,self.high)
        #
    
    def parameters_experiments_init(self):

        self.lineEdit_titleExp.setText("ISR_xBeam_Faraday")
        self.lineEdit_PPS.setText("1")
        self.lineEdit_IPP.setText("10000")
        self.lineEdit_Tx.setText("600")

        self.listWidget_SCode.addItems(["Codigo 28","Barker 13","None"])
        self.listWidget_SCode.setCurrentRow(2)

        self.lineEdit_nCode.setText("0")
        self.lineEdit_nBaud.setText("1")
        self.lineEdit_ndh.setText("10")
        self.lineEdit_nsa.setText("980")
        self.lineEdit_nProfBlock.setText("600")
        self.lineEdit_nBlockFile.setText("10")
        self.lineEdit_SBeam.setText("0xF923")
        self.lineEdit_nFFT.setText("1")
        self.lineEdit_SampleStart.setText("200")
        self.listWidget_files.addItems(["01 us","05 us" ,"10 us"])
        self.listWidget_files.setCurrentRow(0)
        self.lineEdit_User.setText("IGP (D. Scipion)")

    def set_experiment(self):
        
        Title     = self.lineEdit_titleExp.text()
        pps       = float(self.lineEdit_PPS.text())*1000000
        ipp       = float(self.lineEdit_IPP.text())
        nTxA      = float(self.lineEdit_Tx.text())

        if self.listWidget_SCode.currentRow() == 2:
            sCode = None
        elif self.listWidget_SCode.currentRow() == 1:
            sCode = '1111100110101'
        elif self.listWidget_SCode.currentRow() == 0:
            sCode = '1000111100010001000100101101'

        ncode     = float(self.lineEdit_nCode.text())
        nbaud     = float(self.lineEdit_nBaud.text())
        ndh       = float(self.lineEdit_ndh.text())
        nsa       = float(self.lineEdit_nsa.text()) 
        nProfBlock= float(self.lineEdit_nProfBlock.text())
        nBlockFile= float(self.lineEdit_nBlockFile.text())
        
        if len(self.beams) == 0:
            sbeam     = [ i for i in self.lineEdit_SBeam.text().split(",")]
        else:
            sbeam = self.beams
        
        if self.listWidget_files.currentRow() == 0:   files     =     "01"   
        elif self.listWidget_files.currentRow() == 1: files     =     "05"
        elif self.listWidget_files.currentRow() == 2: files     =     "10"
        
        user = self.lineEdit_User.text()
        
        #op = GUI_genExp_AMISR.Parametros(Title,pps,ipp,nTxA,sCode,ncode,nbaud,ndh,nsa,nProfBlock,nBlockFile,sbeam,files,user)
        #GUI_genExp_AMISR.Generate_Experiments(op)
        #print(GUI_genExp_AMISR.Generate_Experiments.path_experiment)
        op = Parametros(Title,pps,ipp,nTxA,sCode,ncode,nbaud,ndh,nsa,nProfBlock,nBlockFile,sbeam,files,user)
        self.experimentos= Generate_Experiments(op)

    def send_exp(self):
        
        self.path_exp = self.experimentos.path_experiment
        ruta = "scp -r %s soporte@%s:/home/soporte/Downloads"%(self.path_exp,self.experimentos.IP)
        print(ruta)
        os.system(ruta)

    
    def add_button(self):

        #self.pushButton_addbeam
        cont = 0
        for item in self.tableWidget_lista.selectedItems():
            
            #print("item:",item.text(),type(item.text()))
            if cont == 0:azi_new = float(item.text())
            elif cont == 1: 
                beam_new = item.text()
                self.beams.append(beam_new)
            elif cont == 2:ele_new = float(item.text())
            cont +=1
        b=""
        for i in self.beams:
            b=b+","+i

        self.lineEdit_SBeam.setText(b[1:])

    def salida(self):
        exit()

    def reset(self):
        self.xcos = []
        self.ycos = []
        self.azimuth_lista = []
        self.elevation_lista = []
        self.beamhexa = []
        self.MplWidget.canvas.axes.clear()
        self.tableWidget_lista.clear()
        self.update_graph2(plot=False)

    def update_graph2(self, azi=180, ele=90,high=[100,500],plot=True):
        ##########################################################################################################
        ##########################################################################################################
        self.azimuth = azi
        self.elevation = ele
        #date = "2023-07-08"
        #date = datetime.strptime(date, '%Y-%m-%d')
        self.high = high
        date = self.fecha
                
        angle = 33
        nptsx = 101
        nptsy = 101



        path4plotname = ''
        self.mesg = ''
        plotname0 = ''
        ptitle= 'AMISR 14'
        ######################## AMISR values
        alfa  = 0.1*numpy.pi/180
        th    = 0.0977
        theta = th*numpy.pi/180
        sina  = numpy.sin(alfa)
        cosa  = numpy.cos(alfa)
        MT1   = numpy.array([[1,0,0],[0,cosa,-sina],[0,sina,cosa]])
        sinb  = numpy.sin(theta)
        cosb  = numpy.cos(theta)
        MT2   = numpy.array([[cosb,sinb,0],[-sinb,cosb,0],[0,0,1]])
        MT3   = numpy.array(numpy.dot(MT2, MT1)).transpose()

        xg    = numpy.dot(MT3.transpose(),numpy.array([1,0,0]))
        yg    = numpy.dot(MT3.transpose(),numpy.array([0,1,0]))
        zg    = numpy.dot(MT3.transpose(),numpy.array([0,0,1])) 

        glat = -11.953371
        glon = -76.874913
        ########################
        cwd = os.getcwd()
        pointings = numpy.genfromtxt(cwd+'/UMET_beamcodes.csv', delimiter=',')
        fullDCOSX = numpy.cos(numpy.radians(pointings[:,2]))*numpy.sin(numpy.radians(pointings[:,1]))
        fullDCOSY = numpy.cos(numpy.radians(pointings[:,2]))*numpy.cos(numpy.radians(pointings[:,1]))


        junkjd = TimeTools.Time(date.year,date.month,date.day).change2julday()
        
        junklst = TimeTools.Julian(junkjd).change2lst(longitude=glon)
        ra_obs = junklst*15

        ObjAnt = AmisrPattern(self.azimuth,
                            self.elevation,
                            maxphi=angle,
                            nptsx=nptsx,
                            nptsy=nptsy,
                            just_rx=False)
        # self.MplWidget.canvas.axes = self.MplWidget.canvas.axes()

        self.PlotApuntes(jd=junkjd,ra_obs=ra_obs,xg=xg, yg=yg,x=ObjAnt.dcosx,y=ObjAnt.dcosy,
                        allAmisr_x=fullDCOSX,allAmisr_y=fullDCOSY)
        self.PlotPatronRa(amp=ObjAnt.norpattern,x=ObjAnt.dcosx,y=ObjAnt.dcosy,
                    getCut=ObjAnt.getcut,title=ptitle)

        self.PlotBfield(self.fecha, heights=self.high)
        
        self.PlotPatronRa(amp=ObjAnt.norpattern,x=ObjAnt.dcosx,y=ObjAnt.dcosy,
                    getCut=ObjAnt.getcut,title=ptitle)

        self.PlotBfield(self.fecha, heights=self.high)

        if plot == True:
            self.only_points(self.xcos,self.ycos)
        self.MplWidget.canvas.mpl_connect('button_press_event', self.on_click)

        if self.MplWidget.canvas.axes.can_zoom():
            print("Ingreso al ZOOM")
            print(self.MplWidget.canvas.axes.can_zoom())
        #plt.show()
        # .clear()
        # self.MplWidget.canvas.axes.plot(t, cosinus_signal)
        # self.MplWidget.canvas.axes.plot(t, sinus_signal)
        #self.MplWidget.canvas.axes.legend(('cosinus', 'sinus'),loc='upper right')
        #self.MplWidget.canvas.axes.set_title('Cosinus - Sinus Signal')
        self.MplWidget.canvas.draw()     

    def PlotApuntes(self,jd=2452640.5,ra_obs=None,xg=None, yg=None,x=None,y=None,
                    allAmisr_x=[],allAmisr_y=[]):

        mindec = -45; maxdec = 25; incdec= 4
        minha = -80; maxha = 80; incha= 6

        ndec = int((maxdec - mindec)/incdec) + 1
        nha =  int((maxha - minha)/incha) + 1
        ha_axes = numpy.reshape(numpy.arange(nha)*incha + minha,(nha,1))
        ones_dec = numpy.reshape(numpy.zeros(ndec) + 1,(ndec,1))
        ha_axes = numpy.dot(ha_axes,ones_dec.transpose())
        ha_axes2 = numpy.array(ra_obs - ha_axes)

        dec_axes = numpy.reshape(numpy.arange(ndec)*incdec + mindec,(ndec,1))
        ones_ra = numpy.reshape(numpy.zeros(nha) + 1,(nha,1))
        dec_axes = numpy.dot(ones_ra,dec_axes.transpose())
        dec_axes2 = numpy.array(dec_axes)

        ObjHor = Astro_Coords.Equatorial(ha_axes2,dec_axes2,jd)
        [alt,az,ha] = ObjHor.change2AltAz()

        z = numpy.transpose(alt)*Misc_Routines.CoFactors.d2r  ; z = z.flatten()
        az = numpy.transpose(az)*Misc_Routines.CoFactors.d2r  ; az = az.flatten()

        vect = numpy.array([numpy.cos(z)*numpy.sin(az),numpy.cos(z)*numpy.cos(az),numpy.sin(z)])

        xg = numpy.atleast_2d(xg)
        dcosx = numpy.array(numpy.dot(xg,vect))
        yg = numpy.atleast_2d(yg)
        dcosy = numpy.array(numpy.dot(yg,vect))

        mcosx = dcosx.reshape(ndec,nha)
        mcosy = dcosy.reshape(ndec,nha)

        # Defining NAN for points outof limits.
        xmax = numpy.max(x)
        xmin = numpy.min(x)
        ymax = numpy.max(y)
        ymin = numpy.min(y)

        factor = 1.3

        noval = numpy.where((mcosx>(xmax*factor)) | (mcosx<(xmin*factor)))
        if noval[0].size>0:mcosx[noval] = numpy.nan
        noval = numpy.where((mcosy>(ymax*factor)) | (mcosy<(ymin*factor)))
        if noval[0].size>0:mcosy[noval] = numpy.nan
    
        # Plotting HA and declination grid.
        iha0 = int((0 - minha)/incha)
        idec0 = int((-14 - mindec)/incdec)

        #fig = Figure(figsize=(8,8), facecolor='white')
        #ax =  fig.add_subplot(111)  
        ### PLOTEO 
        #fig,ax = plt.subplots()
        colorgrid = (1.,109/255.,0)
        # self.MplWidget.canvas.axes.plot(mcosx.transpose(),mcosy.transpose(),color=colorgrid,linestyle='--', lw=0.5)
        self.MplWidget.canvas.axes.plot(mcosx.transpose(),mcosy.transpose(),color=colorgrid,linestyle='--', lw=0.5)
        for idec in numpy.arange(ndec):
            if idec != idec0:
                valx = (mcosx[idec,iha0]<=xmax) & (mcosx[idec,iha0]>=xmin)
                valy = (mcosy[idec,iha0]<=ymax) & (mcosy[idec,iha0]>=ymin)
                if valx & valy:
                    text = str(int(mindec + incdec*idec))+'$^o$'
                    # self.MplWidget.canvas.axes.text(mcosx[idec,iha0],mcosy[idec,iha0],text)
                    self.MplWidget.canvas.axes.text(mcosx[idec,iha0],mcosy[idec,iha0],text)

        # self.MplWidget.canvas.axes.plot(mcosx,mcosy,color=colorgrid,linestyle='--',lw=0.5)
        self.MplWidget.canvas.axes.plot(mcosx,mcosy,color=colorgrid,linestyle='--',lw=0.5)
        for iha in numpy.arange(nha):
            if iha != iha0:
                valx = (mcosx[idec0,iha]<=xmax) & (mcosx[idec0,iha]>=xmin)
                valy = (mcosy[idec0,iha]<=ymax) & (mcosy[idec0,iha]>=ymin)
                if valx & valy:
                    text = str(int(minha + incha*iha))+"'"
                    # self.MplWidget.canvas.axes.text(mcosx[idec0,iha],mcosy[idec0,iha],text)
                    self.MplWidget.canvas.axes.text(mcosx[idec0,iha],mcosy[idec0,iha],text)

        
        if len(allAmisr_x) > 0 and len(allAmisr_y) > 0:
            # self.MplWidget.canvas.axes.scatter(allAmisr_x, allAmisr_y, c='yellow', marker='x', s = 40)
            self.MplWidget.canvas.axes.scatter(allAmisr_x, allAmisr_y, c='yellow', marker='x', s = 40)
        #plt.show()
        print("")
##########################################################################################################
##########################################################################################################
    def PlotPatronRa(self, amp=None,x=None,y=None,getCut=None,title=""):
    
        if getCut == 1:
            return

        xmax = numpy.max(x)
        xmin = numpy.min(x)
        ymax = numpy.max(y)
        ymin = numpy.min(y)

        levels = numpy.array([1e-3,1e-2,1e-1,0.5,1.0])
        tmp = numpy.round(10*numpy.log10(levels),decimals=1)
        labels = list(range(5))
        for i in numpy.arange(5):
            labels[i] = str(int(tmp[i]))

        ### PLOTEO 
        #fig,ax = plt.subplots()
        #colorgrid = (1.,109/255.,0)

        colors = ((0,0,1.),(0,170/255.,0),(127/255.,1.,0),(1.,109/255.,0),(128/255.,0,0))
        if self.site== 1:
            CS = self.MplWidget.canvas.axes.contour(x,y,amp.transpose(),levels,colors=colors)
        else:
            CS = self.MplWidget.canvas.axes.contour(x,y,amp,levels,colors=colors)
        fmt = {}
        for l,s in zip(CS.levels,labels):
            fmt[l] = s

        
        self.MplWidget.canvas.axes.annotate(self.mesg,xy=(0,0),xytext=(0.01,0.01),xycoords='figure fraction')
        self.MplWidget.canvas.axes.clabel(CS,CS.levels,inline=True,fmt=fmt,fontsize=10)
        self.MplWidget.canvas.axes.set_xlim(xmin,xmax)
        self.MplWidget.canvas.axes.set_ylim(ymin,ymax)
        self.MplWidget.canvas.axes.set_title("Total Pattern: " + title)
        if self.site==1:
            self.MplWidget.canvas.axes.annotate('Ng',xy=(-0.05,1.04),xytext=(0.01,0.962),xycoords='axes fraction',arrowprops=dict(facecolor='black', width=1.,shrink=0.2),fontsize=15.)
            self.MplWidget.canvas.axes.set_xlabel("West to South")
            self.MplWidget.canvas.axes.set_ylabel("West to North")
        else:
            self.MplWidget.canvas.axes.set_xlabel("West  to  East")
            self.MplWidget.canvas.axes.set_ylabel("South  to  North")
            self.MplWidget.canvas.axes.grid(True)
    
        #plt.show()
    
    def PlotBfield(self,date,plot=True,heights=[100,500]):

        year = date.year
        month = date.month
        dom = date.day
        doy = datetime(year,month,dom).timetuple().tm_yday
        heights = heights
        #print("Altura BField:",heights)
        
        if heights is None:
            heights = numpy.array([100.,500.,1000.])
        else:
            heights = numpy.array(heights)
        ObjB = BField(year,doy,self.site,heights)
        [dcos, alpha, nlon, nlat] = ObjB.getBField()

        heights = ObjB.heights
        alpha_i = ObjB.alpha_i

        handles = []
        objects = []
        colors  = ['k','m','c','b','g','r','y']
        marker  = ['-+','-*','-D','-x','-s','->','-o','-^']

        alpha_location = numpy.zeros((nlon,2,heights.size))

        for ih in numpy.arange(heights.size):
            alpha_location[:,0,ih] = dcos[:,0,ih,0]
            for ilon in numpy.arange(nlon):
                myx = (alpha[ilon,:,ih])[::-1]
                myy = (dcos[ilon,:,ih,0])[::-1]
                tck = scipy.interpolate.splrep(myx,myy,s=0)
                mydcosx = scipy.interpolate.splev(alpha_i,tck,der=0)

                myx = (alpha[ilon,:,ih])[::-1]
                myy = (dcos[ilon,:,ih,1])[::-1]
                tck = scipy.interpolate.splrep(myx,myy,s=0)
                mydcosy = scipy.interpolate.splev(alpha_i,tck,der=0)
                alpha_location[ilon,:,ih] = numpy.array([mydcosx, mydcosy])

            if plot:
                ObjFig, = self.MplWidget.canvas.axes.plot(alpha_location[:,0,ih],alpha_location[:,1,ih],
                    marker[ih % 8],color=colors[int(ih/8)],ms=5.5,lw=0.5)
                handles.append(ObjFig)
                objects.append(str(heights[ih]) + ' km')        

        if plot:
            legend = self.MplWidget.canvas.axes.legend(handles, objects,loc="lower right", numpoints=1, handlelength=0.3,
                            handletextpad=0.02, borderpad=0.3, labelspacing=0.1)
            self.MplWidget.canvas.axes.add_artist(legend)

            alpha_location = alpha_location
    ###################################################################
    #Evento de MatplotLIB
    def on_click(self,event):
        if event.button is MouseButton.LEFT:
            if event.inaxes:
                x_cosd = event.xdata
                y_cosd = event.ydata
                r = (x_cosd**2+y_cosd**2)**0.5
                
                if r<0.02:
                    azimuth   =  0
                    elevation = 90

                    cwd = os.getcwd()
                    beam,azimuth_r,elevation_r = findRealBeam(azimuth,elevation,path=cwd+'/UMET_beamcodes.csv')
                    beam = "0x{:X}".format(int(beam))
                    self.azimuth_lista.append(azimuth_r)
                    self.elevation_lista.append(elevation_r)
                    self.beamhexa.append(beam)

                    self.add_point(azimuth,elevation,self.MplWidget.canvas.axes)
                    self.MplWidget.canvas.draw()

                else:

                    azimuth = numpy.arctan2(x_cosd,y_cosd)*(180/numpy.pi)
                    elevation = numpy.arccos((x_cosd**2+y_cosd**2)**0.5)*(180/numpy.pi)
                    
                    cwd = os.getcwd()
                    beam,azimuth_r,elevation_r = findRealBeam(azimuth,elevation,path=cwd+'/UMET_beamcodes.csv')
                    
                    beam = "0x{:X}".format(int(beam))
                    #print("azimuth_r",azimuth_r,"elevacion_r",elevation_r,"beam_r",beam)
                    self.azimuth_lista.append(azimuth_r)
                    self.elevation_lista.append(elevation_r)
                    self.beamhexa.append(beam)

                    self.add_point(azimuth_r,elevation_r,self.MplWidget.canvas.axes)
                    print("  ")
                    self.MplWidget.canvas.draw()
           
    def add_point(self,azi,ele,ax):

        x0 = numpy.cos(numpy.radians(ele))*numpy.sin(numpy.radians(azi))
        y0 = numpy.cos(numpy.radians(ele))*numpy.cos(numpy.radians(azi))
        self.xcos.append(x0)
        self.ycos.append(y0)
        self.MplWidget.canvas.axes.scatter(x0, y0, c='red', marker='x', s = 40)
        self.MplWidget.canvas.axes.text(x0, y0,"%s"%(len(self.xcos)-1))
        self.table()

    def delete_point(self):
        
        cont = 0
        for item in self.tableWidget_lista.selectedItems():
            
            if cont == 0:   azi_new   = float(item.text())
            elif cont == 1: beam_new  = item.text()
            elif cont == 2: ele_new   = float(item.text())
            cont +=1

        x0 = numpy.cos(numpy.radians(ele_new))*numpy.sin(numpy.radians(azi_new))
        y0 = numpy.cos(numpy.radians(ele_new))*numpy.cos(numpy.radians(azi_new))
        #points = [(self.xcos[i],self.ycos[i]) for i in range(len(self.xcos))]
        #print("points",points)

        self.xcos.remove(x0)
        self.ycos.remove(y0)
        
        print("azi_new",azi_new,type(azi_new))
        self.azimuth_lista.remove(azi_new)
        self.elevation_lista.remove(ele_new)
        self.beamhexa.remove(beam_new)

        self.MplWidget.canvas.axes.clear()
        try:
            azimuth = float(self.lineEdit_azimuth.text())
            elevation = float(self.lineEdit_elevation.text())
            print("AZIMUTH INGRESADO:",azimuth,type(azimuth))
            print("ELEVATION INGRESADO:",elevation,type(elevation))
        except:
            pass
        
        if len(self.lineEdit_high.text()) == 0:
            self.high = [100,500]
        else:
            self.high = [float(i) for i in self.lineEdit_high.text().split(",")]
        self.get_fecha()

        if len(self.lineEdit_azimuth.text()) != 0:
            self.azimuth = float(self.lineEdit_azimuth.text())
            self.elevation = float(self.lineEdit_elevation.text())
            print("AZIMUTH INGRESADO:",self.lineEdit_azimuth.text())
            print("ELEVATION INGRESADO:",elevation,type(elevation))
            self.update_graph2(azimuth,elevation,self.high)
        else:
            self.update_graph2(self.azimuth,self.elevation,self.high,plot=True)
        self.table()

    def only_points(self,xcos,ycos):
        
        for i in range(len(xcos)):
            self.MplWidget.canvas.axes.scatter(xcos[i],ycos[i], c='red', marker='x', s = 40)
            self.MplWidget.canvas.axes.text(xcos[i], ycos[i],"%s"%(i))

    def table(self):
        self.tableWidget_lista.clear()
        data = {'AZI':self.azimuth_lista,'ELE':self.elevation_lista,'BEAM HEXA':self.beamhexa}
        horHeaders = []
        self.tableWidget_lista.setRowCount(self.row_table)
        self.tableWidget_lista.setColumnCount(3)
        grid = QGridLayout()
        self.setLayout(grid)
        for n, key in enumerate(sorted(data.keys())):
            #print(key)
            horHeaders.append(key)
            for m,item in enumerate(data[key]):
                #print("m",m,"Item",item,type(item))
                newitem = QTableWidgetItem(str(item))
                self.tableWidget_lista.setItem(m,n,newitem)
        verHeaders = ["Beam %s"%i for i in range(self.row_table)]
        self.tableWidget_lista.setHorizontalHeaderLabels(horHeaders)
        self.tableWidget_lista.setVerticalHeaderLabels(verHeaders)
        grid.addWidget(self.tableWidget_lista, 0,0)

app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()
