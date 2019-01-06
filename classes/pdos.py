from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import re
import numpy as np
from scipy.interpolate import CubicSpline, interp1d, PchipInterpolator, Akima1DInterpolator, KroghInterpolator
import matplotlib.pyplot as plt
from scipy.signal import *
from math import *;
from classes.config import pdosColor, pdosXLim, pdosFermi

#---------------------------------
#PDOS Plotter,
#plot wfc pdos files created by Quantum Espresso
#If you want to automate the fermi and x limits insertion, change them in Config.py



class PDOS:
    def __init__(self):
        print("Class created");
        self.dosList = list();
        self.fermi = 0;
        if pdosFermi:
            self.fermi = pdosFermi;
        else:
            self.fermi = 0;

    def findBetween(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""

    # -----------Defining a class for loading PDOS files----------------#
    def loadFiles(self, directory="./", mask="All Files (*.*)"):
        caption = "Open Files";
        fileNames = QFileDialog.getOpenFileNames(None, caption, directory, mask);
        dosFiles = list();

        for file in fileNames[0]:
            if "wfc" in str(file):
                atomNumber = self.findBetween(str(file), "atm#", "(");
                atomSymbol = self.findBetween(str(file), "(", ")_wfc");
                orbital = self.findBetween(str(file), "wfc#", ")")[-1];
                label = "{}({})#{}".format(atomSymbol, orbital, atomNumber);
                dos = np.loadtxt(file, skiprows=0);
                dos[:, 0] = dos[:, 0] - self.fermi;
                dosFiles.append([str(file), atomNumber, atomSymbol, orbital, label, dos]);
            elif "pdos_tot" in str(file):
                atomNumber = "";
                atomSymbol = "All";
                orbital = "";
                label = "All";
                dos = np.loadtxt(file, skiprows=0);
                dos[:, 0] = dos[:, 0] - self.fermi;
                dosFiles.append([str(file), atomNumber, atomSymbol, orbital, label, dos]);
        self.dosList = dosFiles;
        return dosFiles;

    # plotting by interpolating
    def plot(self):
        fig, ax = plt.subplots(1, 1, figsize=(8, 4));
        for i, file in enumerate(self.dosList):
            dos = file[-1];
            b, a = butter(1, 0.035);  # ---filtering the DOS values for smoother plot
            dosFiltered = filtfilt(b, a, dos[:, 1], method="gust");
            if "All" in file[-2]:
                ax.fill_between(dos[:, 0], dosFiltered, zorder=0, color=pdosColor['all'], alpha=0.3);
                ax.plot(dos[:, 0], dosFiltered, label=file[-2], linewidth=0.1, color="gray");
                continue;
            if i < 9:
                ax.plot(dos[:, 0], dosFiltered, label=file[-2], linewidth=0.5,
                        color=pdosColor[i + 1]);  # plotting the dos
            else:
                ax.plot(dos[:, 0], dosFiltered, label=file[-2], linewidth=0.5);  # plotting the dos
        ax.axvline(x=0.0, lw=0.7, color="red")
        ax.set_ylabel("DOS");
        ax.set_xlabel("Energy (eV)");
        if pdosXLim['xmin']:
            ax.set_xlim(left=pdosXLim['xmin']);
        if pdosXLim['xmax']:
            ax.set_xlim(right=pdosXLim['xmax']);
        ax.set_ylim(bottom=0.0);
        plt.legend();
        plt.grid(True);
        plt.show();


if __name__ == "__main__":
    app = QApplication([])
    x = PDOS();
    x.loadFiles();
    x.plot();

    # for this case ...
    app.processEvents()
    # app.exec_()

