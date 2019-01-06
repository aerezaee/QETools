# pylint: disable=C0111,R0902,R0902,W0611,W0301,C0103,C0411

import os
import re
import sys
import xml.etree.ElementTree as ET
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QFileDialog, QMessageBox
import ase;
from ase import Atoms;
from ase.io import read, write;
from ase.visualize import view;
from collections import Counter;

uiMainWindow, QtBaseClass = uic.loadUiType("./classes/inputmaker.ui")


class App(QtWidgets.QMainWindow, uiMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        uiMainWindow.__init__(self)
        self.setupUi(self)
        self.chooseFileBtn.clicked.connect(self.chooseFileBtnHandler);
        self.saveBtn.clicked.connect(self.saveBtnHandler);
        self.viewBtn.clicked.connect(self.viewBtnHandler);
        # Define Files
        self.atoms = "";  # ase type atoms class
        self.inputs = ""
        self.outputs = ""
        self.fileOpened = False
        self.cell = "";
        self.atomsDF = 0;
        self.labels = {};
        self.locations = [];
        self.controlBlock = {"$calculation": 'scf',
                             "$pseudo_dir": './ps/',
                             "$prefix": 'first',
                             "$outdir": './out/',
                             "$verbosity": 'low',
                             "$nstep": 1000,
                             "$restart_mode": 'from_scratch',
                             "$etot_conv_thr": "1e-6",
                             "$forc_conv_thr": "1e-3",
                             }

        self.systemBlock = {"$ibrav": 0,
                            "$nat": 99,
                            "$ntyp": 2,
                            "$ecutwfc": 30,
                            "$ecutrho": 120,
                            "$input_dft": 'PBE',
                            "$occupations": 'smearing',
                            "$smearing": "mp",
                            "$degauss": 0.0012,
                            }
        self.others = {
            "$ion_dynamics": "bfgs",
            "$cell_dynamics": "bfgs",
            "$cell_factor": 5
        }

        self.electronsBlock = {"$diagonalization": 'david',
                               "$mixing_mode": 'plain',
                               "$mixing_beta": 0.7,
                               "$conv_thr": 0.000001,
                               "$electron_maxstep": 1000,
                               "$scf_must_converge": "false"
                               }
        self.inputParameters = {
            **self.controlBlock, **self.systemBlock, **self.electronsBlock, **self.others}

    def saveBtnHandler(self):
        try:
            self.getValues();
            directory = self.fileChooser(type="directory");
            if (self.scfFile.isChecked()): self.inputChanger(type='scf', directory=directory)
            if (self.bandsFile.isChecked()): self.inputChanger(type='bands', directory=directory)
            if (self.relaxationFile.isChecked()): self.inputChanger(type="vc-relax", directory=directory)
            if (self.dosFile.isChecked()): self.inputChanger(type="dos", directory=directory)
            if (self.pdosFile.isChecked()): self.inputChanger(type="pdos", directory=directory)
            self.psFiles(directory=directory);
        except Exception as e:
            print(str(e));

    def getValues(self):
        self.paramChanger(
            ['$pseudo_dir', '$prefix', '$outdir', '$nstep', '$restart_mode', '$etot_conv_thr', '$forc_conv_thr'],
            [self.pseudo_dir.text(), self.prefix.text(), self.outdir.text(), self.nstep.text(),
             self.restart_mode.currentText(), self.etot_conv_thr.text(), self.forc_conv_thr.text()]);
        self.paramChanger(
            ['$nat', '$ntyp', '$ecutwfc', '$ecutrho', '$input_dft', '$occupations', '$smearing', '$degauss'],
            [self.nat.text(), self.ntyp.text(), self.ecutwfc.text(), self.ecutrho.text(), self.input_dft.text(),
             self.occupations.currentText(), self.smearing.currentText(), self.degauss.text()])
        self.paramChanger(['$diagonalization', '$mixing_mode', '$mixing_beta', '$conv_thr', '$electron_maxstep',
                           '$scf_must_converge'],
                          [self.diagonalization.currentText(), self.mixing_mode.currentText(), self.mixing_beta.text(),
                           self.conv_thr.text(), self.electron_maxstep.text(), self.scf_must_converge.currentText()])
        self.paramChanger(['$ion_dynamics', '$cell_dynamics', '$cell_factor'],
                          [self.ion_dynamics.currentText(), self.cell_dynamics.currentText(), self.cell_factor.text()]);

    def inputParametersMaker(self):
        self.inputParameters = {
            **self.controlBlock, **self.systemBlock, **self.electronsBlock, **self.others}

    def paramChanger(self, params, newValues):
        """Used to change parameters, params and newValue are lists
        like:self.paramChanger(['$nat],[5])"""

        for i, param in enumerate(params):
            for block in [self.controlBlock, self.systemBlock, self.electronsBlock, self.others]:
                for key, value in block.items():
                    if (key == param):
                        block[key] = newValues[i]
        self.inputParametersMaker()

    def inputChanger(self, type='scf', directory="./outputs/"):
        inputPath = "./inputs/{}.in".format(type)
        outputPath = "{}/{}.in".format(directory, type)
        print(directory, outputPath);
        self.inputParametersMaker()
        file = open(inputPath)
        fileText = file.read()
        file.close()
        atomLocations = "";
        fileText = fileText.replace("$atomicLocations", self.positions.toPlainText())

        fileText = fileText.replace("$cellparameters", self.cellparameters.toPlainText());

        atomicText = "";
        for symbol, mass in self.masses.items():
            atomicText += "{}\t{:3.6f}\t{}.UPF\n".format(symbol, mass, symbol);
        fileText = fileText.replace("$species", atomicText);

        for key, value in self.inputParameters.items():
            fileText = fileText.replace(key, str(value))

        if (type in ['scf', 'vc-relax', 'dos', 'pdos']):
            fileText = fileText.replace("$kepointType", "automatic")
            fileText = fileText.replace("$kpoints", self.kpoints.text())
        if (type == 'bands'):
            fileText = fileText.replace("$kepointType", "crystal_b")
            fileText = fileText.replace("$kpoints", self.kpointsBand.toPlainText());
        file = open(outputPath, mode="w")
        file.writelines(fileText)
        file.close()

    def chooseFileBtnHandler(self):
        fileName = self.fileChooser();
        try:
            self.readFile(fileName);
            self.saveBtn.setEnabled(True);
            self.viewBtn.setEnabled(True);
        except Exception as e:
            self.errorMessage("Please Select a Acceptable File (CONTCAR,OUTCAR,CIF)", "Error")

    def viewBtnHandler(self):
        #ase.visualize.view(self.atoms);
        self.atoms.edit();
        cellText = "";
        for line in self.atoms.get_cell():
            cellText += "{:4.6f}\t{:4.6f}\t{:4.6f}\n".format(line[0], line[1], line[2])
        self.cellparameters.setPlainText(cellText);

    def fileChooser(self, type="open"):
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

        def inputMaker(self, directory="./outputs/"):
            self.paramChanger(["$nat", "$ntyp"], [self.nat, len(self.masses)])
            self.inputChanger(type='scf', directory=directory)
            self.inputChanger(type='bands', directory=directory)
            self.inputChanger(type="vc-relax", directory=directory)
            self.inputChanger(type="dos", directory=directory)
            self.inputChanger(type="pdos", directory=directory)

    def readFile(self, fileName):
        ''' For reading files and convert them to a ASE Atoms object'''
        self.atoms = 0;
        self.atoms = read(fileName);
        atomLabels = Counter(self.atoms.get_chemical_symbols());
        self.labels = atomLabels;
        self.masses = {};

        nat = 0;
        for sym, value in atomLabels.items():
            self.masses[sym] = Atoms(sym).get_masses()[0];
            nat += value;
        self.nat.setText(str(nat));  # make number of atoms and types in GUI
        self.ntyp.setText(str(len(atomLabels)));
        labels = self.atoms.get_chemical_symbols();
        pos = self.atoms.get_scaled_positions().tolist();
        self.locations = [];
        for i, line in enumerate(pos):
            self.locations.append([labels[i]] + line);
        atomLocations = "";

        for line in self.locations:  # updating the cell and positions in GUI
            atomLocations += "{}\t{:2.8f}\t{:2.8f}\t{:2.8f}\n".format(line[0], line[1], line[2], line[3]);
        self.positions.setPlainText(atomLocations);

        cellText = "";
        for line in self.atoms.get_cell():
            cellText += "{:4.6f}\t{:4.6f}\t{:4.6f}\n".format(line[0], line[1], line[2])
        self.cellparameters.setPlainText(cellText);

    def errorMessage(self, text, title):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(title)
        msg.setFixedSize(100, 300)
        msg.setInformativeText(text)
        msg.setWindowTitle(title)
        msg.exec();

    def psFiles(self, directory=""):
        import os.path;
        from shutil import copyfile;
        dir = "./inputs/ps/";
        fileNames = [];
        for el in self.labels.keys():
            fileName = dir + str(el) + ".UPF";
            os.makedirs(directory + "/ps/", exist_ok=True);
            if os.path.isfile(fileName):
                outputFile = directory + "/ps/" + str(el) + ".UPF";
                copyfile(fileName, outputFile)
                print(fileName, outputFile);
            else:
                self.errorMessage("PseudoPotential Files Not Found, Please Copy Them Manually", "File Not Found");
                return 0;


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
