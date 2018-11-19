import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import numpy as np
import scipy
import os

import matplotlib.pyplot as plt
import pandas as pd

directoryPath = "";

uiMainWindow, QtBaseClass = uic.loadUiType("extract.ui")

class ExtractrApp(QtWidgets.QMainWindow, uiMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uiMainWindow.__init__(self)
        self.setupUi(self)
        self.numberOfLevelsToScan = 0;
        self.type = "Quantum Espresso";
        self.fileType = {"VASP": "OUTCAR", "Quantum Espresso": "out"};
        self.energyText = {"VASP": "  free  energy   TOTEN  = ", "Quantum Espresso": "!    total energy              ="}
        self.values = pd.DataFrame(columns=['File', 'Energy', 'Diff Energy']);

        self.chooseDirectory.clicked.connect(self.chooseDirectoryHandler);
    ############################Define the event handlers

    def chooseDirectoryHandler(self):
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"));
        self.directoryPathLabel.setText(file);
        self.fileLister(file);

    def saveEvent(self):
        print("save");
        file, _ = QFileDialog.getSaveFileName(self, "Select File To save");
        if file:
            with open(file, 'w') as f:
                self.values.to_csv(file)

    ##################################################Define the Methods
    def fileLister(self, directoryName):
        self.fileNames = list()
        self.paths = list();
        # Energy = list()
        self.Energy = np.empty(0, dtype=np.float64);
        self.directory = list()
        for root, dirs, files in os.walk(directoryName):
            if root[len(directoryName) + 1:].count(os.sep) <= self.numberOfLevelsToScan:
                for file in files:
                    if file==self.fileName.text():
                        self.directory.append(root.replace(str(directoryName), "").replace(str(os.sep), "",
                                                                                           1));  # appending only dir name
                        self.paths.append(root.replace(".//", "").replace("\\", "/"))  # appending he full path
                        self.Energy = np.append(self.Energy, [
                            float(self.energyFinder(os.path.join(root, file)))])  # appending the Total Energy
        if (len(self.Energy) > 0):
            minEnergy = np.min(self.Energy);
            print(self.Energy, minEnergy);
            self.diffEnergy = self.Energy - minEnergy;
            print(self.diffEnergy);
            d = {'File': self.directory, 'Energy': self.Energy, 'Diff Energy': self.diffEnergy};
            self.values = pd.DataFrame(d);
            self.values['File'] = self.values['File'].astype('category');
            self.updatingTable(clearing=False);
        else:
            d = {'File': [], 'Energy': [], 'Diff Energy': []};
            self.values = pd.DataFrame(d);
            self.updatingTable(clearing=True);
            self.outputText.setText("No OUTCAR file found");

    def energyFinder(self, file):
        E = 0
        for line in open(file):
            if self.energyText[self.type] in line:
                words = line.split()
                E = words[4]
        return E

    def updatingTable(self, clearing=False):
        self.clearingTable(self.outputTable);
        if clearing == False:
            for i, dir in enumerate(self.directory):
                self.outputTable.insertRow(i);
                self.outputTable.setItem(i, 0, QTableWidgetItem(dir));
                print(self.Energy[i]);
                self.outputTable.setItem(i, 1, QTableWidgetItem(str(self.Energy[i])));
                self.outputTable.setItem(i, 2, QTableWidgetItem(str(self.diffEnergy[i])));
        else:
            # while (self.outputTable.rowCount() > 0):
            #     self.outputTable.removeRow(0);
            self.clearingTable(self.outputTable);

    def clearingTable(self, table):
        while (table.rowCount() > 0):
            table.removeRow(0);

    def plotting(self, xIndex, yIndex, title=""):
        plt.close();
        x = self.values[self.values.columns[xIndex]].cat.codes;
        y = self.values[self.values.columns[yIndex]];

        # smoothing
        from scipy.interpolate import CubicSpline
        bci = CubicSpline(x, y, extrapolate=False)
        xNew = np.linspace(min(x), max(x), 1000)
        yNew = bci(xNew)

        plt.scatter(x, y, linewidth=3, marker='^')
        plt.plot(xNew, yNew, 'r', linewidth=1, alpha=0.5);
        columnNames = self.values.columns;
        plt.xlabel(columnNames[xIndex]);
        plt.ylabel(columnNames[yIndex]);

        plt.grid(True);
        plt.show();



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ExtractrApp()
    window.show()
    sys.exit(app.exec_())