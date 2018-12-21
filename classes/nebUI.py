from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QFileDialog,QMessageBox
import os
from classes.nebPlotter import  nebPlotter;
import sys;

uiMainWindow, QtBaseClass = uic.loadUiType("./classes/nebUI.ui")

class nebApp(QtWidgets.QMainWindow, uiMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uiMainWindow.__init__(self)
        self.setupUi(self)
        #UI's components:
        #Button: plotBtn, #outout:nebOutput, #input: nebInput #sep: sepCombo #xRangeInput, yRangeInput

        self.plotBtn.clicked.connect(self.plotBtnHandler);
        self.nebObject = 0;
    def plotBtnHandler(self):
        #try:
        energyText = self.nebInput.toPlainText();
        locationText = self.nebLocationInput.toPlainText();
        label = self.labelInput.text();
        highestArrow = self.arrowChk.isChecked();
        sep = self.sepCombo.currentText();
        if sep == "\\n":
            sep = os.linesep;
        print(sep);
        self.nebObject = 0;
        self.nebObject = nebPlotter(energyText=energyText,locationText = locationText,sep=sep,highestArrow=highestArrow, label = label);
        self.nebOutput.setPlainText(str(self.nebObject));
        self.nebObject.plot(xUnit = self.xUnit.text(), yUnit= self.yUnit.text());
        #except Exception as e:
            #self.nebOutput.setPlainText("Please enter values and choose separator in correct format and sequence");
            #print (str(e));

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = nebApp()
    window.show()
    sys.exit(app.exec_())