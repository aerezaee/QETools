# pylint: disable=C0111,R0902,R0902,W0611,W0301,C0103,C0411
import sys;
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
from classes.cutoff import *;
import matplotlib.pyplot as plt;
from scipy.signal import *;
import numpy as np


uiMainWindow, QtBaseClass = uic.loadUiType("classes/cutoff.ui")

class cutOffApp(QtWidgets.QMainWindow, uiMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uiMainWindow.__init__(self)
        self.setupUi(self)
        self.openBtn.clicked.connect(self.openBtnHandler);
        self.plotBtn.clicked.connect(self.plotBtnHander);
        self.value = 0;
        self.cutoff = [];
        self.qe = 0;#holder for QEObject
    def openBtnHandler(self):
        value = 4;
        cutoff = eval(self.energyEdit.text());
        runCommand = self.runCommand.text().split();
        print(value,type(value),runCommand);
        fileName = self.fileChooser();
        self.qe = QeRun(inputFile = fileName);
        self.qe.inputMaker(steps = cutoff,runCommand= runCommand);
        self.outputMaker();
    
    def outputMaker(self):
        text = "";
        for i in range(len(self.qe.energies)):
            text = text + "{:3.1f} eV: {:12.5f} eV\n".format(self.qe.cutoff[i],self.qe.energies[i]);
        self.outputText.setPlainText(text);
    def plotBtnHander(self):
        try:
            if len(self.qe.energies) > 2:
                from scipy.interpolate import CubicSpline,interp1d,PchipInterpolator,Akima1DInterpolator,KroghInterpolator
                x = self.qe.cutoff;
                bci = interp1d(x, self.qe.energies, kind = "quadratic");
                xNew = np.linspace(min(x), max(x), 1000)
                yNew = bci(xNew)
                plt.plot(xNew,yNew,linewidth = 0.3);
                plt.scatter(self.qe.cutoff,self.qe.energies,linewidth = 2);

                plt.xlabel("Cutoff Energies (eV)");
                plt.ylabel("Energy (eV)");
                plt.show();
            else:
                plt.scatter(self.qe.cutoff,self.qe.energies,linewidth = 2);
                plt.plot(self.qe.cutoff,self.qe.energies,linewidth = 0.3);
                plt.xlabel("Cutoff Energies (eV)");
                plt.ylabel("Energy (eV)");
                plt.show();
        except Exception as e:
            print (str(e));

    def fileChooser(self, type="open"): # for choosing file and directory
        fileName = ""
        if type == "open":
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "QFileDialog.getOpenFileName()", "", "All Files (*);;XML Files (*.xml)")
        if type == "save":
            fileName, _ = QtWidgets.QFileDialog.getSaveFileName(
                self, "QFileDialog.getSaveFileName()", "", "All Files (*);;Text Files (*.txt)")
        if type == "directory":
            fileName = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        print(fileName)
        return fileName
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = cutOffApp()
    window.show()
    sys.exit(app.exec_())
