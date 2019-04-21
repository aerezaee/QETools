# pylint: disable=C0111,R0902,R0902,W0611,W0301,C0103,C0411
import pip

pkgs = ['PyQt5', 'ase']
for package in pkgs:
    try:
        exec("import {}".format(package));
    except ImportError as  e:
        print("Needs to install needed packages, install {}".format(package));
        ans = input("Y for Yes, Others for No\n");
        if ans.lower() == "y":
            import subprocess

            subprocess.check_call(["python", '-m', 'pip', 'install', package])  # install pkg
        else:
            exit();

import os
import re
import sys
import xml.etree.ElementTree as ET
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
import classes.inputMaker as inputMaker;
from classes.espressoParser import *;
from classes.nebUI import *;
from classes.pdos import *;
from classes.cutoffUI import *;
from classes import config
import json
from configparser import ConfigParser

uiMainWindow, QtBaseClass = uic.loadUiType("ui.ui")


class App(QtWidgets.QMainWindow, uiMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uiMainWindow.__init__(self)
        self.setupUi(self)
        self.openXMLBtn.clicked.connect(self.oepnXMLBtnHandler)
        self.plotBandBtn.clicked.connect(self.plotBandBtnHandler)
        self.saveBtn.clicked.connect(self.saveBtnHandler)
        self.viewBtn.clicked.connect(self.viewBtnHandler)
        self.dosPlotBtn.clicked.connect(self.dosPlotBtnHandler)
        self.convertBtn.clicked.connect(self.convertBtnHandler)
        self.occupationSpin.valueChanged.connect(self.occupationSpinHandler)
        self.nebBtn.clicked.connect(self.nebBtnHandler);
        self.pdosBtn.clicked.connect(self.pdosBtnHandler);
        self.cutoffBtn.clicked.connect(self.cutoffBtnHandler);
        self.config = ConfigParser();
        self.config.read("config.ini");
        # Define Files
        self.fileLocation = ""
        dir = self.config.get("run","directory");
        if (dir == ""):
            self.directory = os.path.dirname(os.path.realpath(__file__))
            self.saveConfig(section = "run",key = "directory",value = self.directory);
        else:
            self.directory = dir;
        #Get values from Config.ini files and put them in the input text boxes
        self.yRange = eval(self.config.get("run","yRange"));
        self.xTicks = self.config.get("run","xTicks").replace("\"","").replace("\'","").replace(" ","");
        self.xTicksLocations = self.config.get("run","xTicksLocations");
        self.yRangeInput.setText(str(self.yRange).replace("[","").replace("]",""));#yInputText
        self.directoryLabel.setText(str(self.directory));
        self.xRangeInput.setText(str(self.xTicks).replace("[","").replace("]","").replace("\"",""));
        self.xTicksLocationInput.setText(str(self.xTicksLocations).replace("[","").replace("]",""));
    
        self.xmlFile = "";
        self.inputs = "";
        self.outputs = "";
        self.fileOpened = False

    def saveConfig(self,configFile = "config.ini",section = "run",key = "directory", value = ""):
        if ((key == "directory") and (value == "")):
            value = self.directory;
        self.config.set(section,key,str(value));
        file = open(configFile,"w+");
        self.config.write(file);
        file.close()
    def oepnXMLBtnHandler(self):

        self.xmlFile = self.fileChooser(type="open")
        if (str(self.xmlFile).lower().endswith(".xml")):
            self.directory = os.path.dirname(os.path.abspath(self.xmlFile))
            self.saveConfig();
            self.directoryLabel.setText(str(self.directory))
            self.plotBandBtn.setEnabled(True)
            self.saveBtn.setEnabled(True)
            self.viewBtn.setEnabled(True)
            self.start()
        else:
            self.errorMessage("File Selection Error", "Please Select a XML File Created By QE ")

    def plotBandBtnHandler(self):
        try:
            #self.yRange = eval(self.yRangeInput.text())
            self.yRange = [float(i) for i in self.yRangeInput.text().split(",")];
            self.outputs.yLim = self.yRange
        except  Exception as e:
            self.errorMessage("Wrong Value", "Please enter the range as ymin,ymax like -1,1");

        try:
            self.xTicks = self.xRangeInput.text().replace(" ","").replace("\"","").split(",");
        except Exception as e:
            self.errorMessage("Wrong Value", "Please enter the range as G,X,Y,Z");
        try:
            xTicksLocations = eval(self.xTicksLocationInput.text());
            print ("xTickslocations:",xTicksLocations,self.xTicks,self.xTicksLocationInput.text())
            if len(xTicksLocations) == len(self.xTicks) and np.max(xTicksLocations) <= self.outputs.nKPoints:
                self.xTicksLocations = xTicksLocations;
            else:
                raise Exception("Error");

        except Exception as e:
            self.xTicksLocations = np.linspace(0, self.outputs.nKPoints - 1, num=len(self.xTicks));
            self.errorMessage("Value Problem",
                              "Please Enter the ticks locations in proper format and compatible with tick labels");


        self.outputs.tickLabels = self.xTicks;
        self.outputs.tickLocations = self.xTicksLocations;
        
        self.saveConfig(key = "xTicks",value = self.xTicks);
        self.saveConfig(key = "xTickLocations",value = self.xTicksLocations);
        self.saveConfig(key = "yRange",value = self.yRange);
        self.outputs.plotBand(usingAntonate=self.showBandCB.isChecked(), usingLines=self.showLinesCB.isChecked(), usingXTicks=self.xTicksCB.isChecked())

    def saveBtnHandler(self):
        fileName = self.fileChooser(type="save")
        self.outputs.saveOutput(outputFile=fileName)
    def nebBtnHandler(self):
        self.nebPlotter = nebApp();
        self.nebPlotter.show();

    def dosPlotBtnHandler(self):
        try:
            fileName = self.fileChooser(type="open")
            outputResults.dosPlotter(filePath=fileName, a=1, b=0.02, usingTicks=self.yTicksCB.isChecked());
        except Exception as e:
            self.errorMessage("Please Choose a DOS File Created by DOS.X", "Wrong File Format");

    def viewBtnHandler(self):
        self.outputs.view()

    def occupationSpinHandler(self): ##Handling
        if (self.fileOpened == True):
            self.start()

    def convertBtnHandler(self):
        self.inputMaker = inputMaker.App();
        self.inputMaker.show();

    def pdosBtnHandler(self):
        pdos = PDOS();
        pdos.loadFiles();
        pdos.plot();

    def cutoffBtnHandler(self):
        self.cutoff = cutOffApp();
        self.cutoff.show();

    ###############
    def errorMessage(self, text, title):  # text: the text of messagebox and title is the title of messagebox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(title)
        msg.setFixedSize(100, 300)
        msg.setInformativeText(text)
        msg.setWindowTitle(title)
        msg.exec();

    def fileChooser(self, type="open"): # for choosing file and directory
        fileName = ""
        if type == "open":
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "QFileDialog.getOpenFileName()", self.directory, "All Files (*);;XML Files (*.xml)")
        if type == "save":
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "QFileDialog.getSaveFileName()", self.directory, "All Files (*);;Text Files (*.txt)")
        if type == "directory":
            fileName = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print(fileName)
        return fileName

    def start(self):
        self.fileOpened = True
        self.outputs = outputResults(
            fileName = self.xmlFile, path=self.directory, occu=float(self.occupationSpin.text()))
        self.outputText.setPlainText("")
        try:
            self.outputText.setPlainText(str(self.outputs))
        except Exception as e:
            self.outputText.setPlainText(str(e));

        #ticks = np.linspace(0, self.outputs.nKPoints - 1, num=len(self.xTicks), dtype=int).tolist();
        #self.xTicksLocationInput.setText(str(ticks).replace("[", "").replace("]", ""));



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
    
