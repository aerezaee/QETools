import tkinter as tk
import xml.etree.ElementTree as ET
from tkinter import filedialog
import os;
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import NullFormatter
from scipy.signal import *
from ase import Atoms, Atom;
from ase.visualize import view;
from ase.dft.kpoints import get_special_points
from ase.dft.kpoints import bandpath
from ase.data import covalent_radii
from math import sqrt;



class outputResults:
    def __init__(self, fileName, occu=1, path=""):
        self.semiConductorType = 'None';    #type of material
        self.directBandGap = "True";        #if the bandgap is direct
        self.bandGap = 0;                   #value of bandgap
        self.fermiEnergy = 0;               #value of fermi energy
        self.eigenValues = [];              #value of eigen values of band structure
        self.occupations = [];              #value of occupations for any of eigen values
        self.nKPoints = 0;                  #Number of kpoints for calculating the eigenvalues
        self.kPoints = [];                  #the kpoints used to calculate the eigenvalues
        self.nband = 0;                     #number of bands
        self.nAtomicWFC = 0;                #number of atomic wfcs
        self.sfSteps = 0;                   #number of steps for relaxation calculation
        self.numberOfAtoms = 0;             #number of atoms
        self.alat = 1;                      #lattice constant
        self.locations = 0;                 #locations of atoms (pandas DF)
        self.cell = [];                     #cell vectors (3x3)
        self.cellDimension = [];            #cell dimensions (3x1)
        self.totalEnergy = 0;               #total energy of structure
        self.yLim = [-1,1];                 #y range for plotting
        self.dos = "";                      #variable for keeping dos (Pandas DF)
        self.atoms = "";                    #ASE atoms object
        self.elements = {};                 #list of elements as a dictionary
        self.directory = path;              #working directory
        self.const = Constants();           #Constnats values
        self.occu = occu;                   #occupation criteria for calculating the band gap
        self.fileName = fileName;
        self.bonds = [];
        self.staticsDatas = [];              #contains the statistics of Bond Lengths
        self.atomLabels = "";                #Contains the atom labels ans their number

        self.tickLabels = ['G','X','Y','Z','G'];    #tick labels
        self.tickLocations = [];
        self.bondLengthes = [];
        self.calculation();

    def calculation(self):
        fileName = self.fileName;
        tree = ET.parse(fileName);
        root = tree.getroot()
        outputNode = "";
        bandStructureNode = "";
        atomPositionsNode = "";


        for child in root:
            if child.tag == "output":
                outputNode = child;
        for child in outputNode:
            if child.tag == "band_structure":
                bandStructureNode = child;
        for energy in outputNode.iter("etot"):
            self.totalEnergy = float(energy.text)*self.const.ry2ev;
        bands = [];
        for band in bandStructureNode.iter("eigenvalues"):
            bands.append([float(eigen) * self.const.h2ev for eigen in band.text.split()]);
        self.eigenValues = np.transpose(np.array(bands));

        occupations = [];
        for occupation in bandStructureNode.iter("occupations"):
            occupations.append([float(eigen) for eigen in occupation.text.split()]);
        self.occupations = np.transpose(np.array(occupations));
        for energy in bandStructureNode.iter("fermi_energy"):
            self.fermiEnergy = float(energy.text) * self.const.h2ev;

        for nks in bandStructureNode.iter("nks"):   #Get the number of bands
            self.nKPoints = int(nks.text);
        for nks in bandStructureNode.iter("nk"):
            self.nKPoints = int(nks.text);

        atomicPositionNode = "";    #extracting the positions and atoms
        cellNode = "";
        for child in outputNode:
            if child.tag == "atomic_structure":
                self.numberOfAtoms = int(child.attrib['nat']);
                for c in child:
                    if c.tag == "atomic_positions":
                        atomicPositionNode = c;
                    if c.tag == "cell":
                        cellNode = c
        atoms = Atoms();
        for atom in atomicPositionNode.iter('atom'):
            name = atom.attrib['name'];
            index = int(atom.attrib['index']);
            pos = [float(pos)*self.const.au2ang for pos in atom.text.split()];
            atoms.append(Atom(name, (pos[0], pos[1], pos[2])));
        atoms.set_pbc((False, False, False));
        self.atoms = atoms;
        cellTexts = ["a1", "a2", "a3"];
        for a in cellTexts:
            for vec in cellNode.iter(a):
                print (vec)
                self.cell.append([float(v)*self.const.au2ang for v in vec.text.split()]);# using au2ang to convert au to angstrom
        self.atoms.set_cell(self.cell);

        self.bandCalculator();
        self.bondsCalculator();

    def bandCalculator(self):

        cutZero = 0; #finding the band that pass the fermi-band
        cutZeroType = "";
        maxValue = -1000;
        minValue = 1000;
        cBand = self.eigenValues[-1];cBandNumber = 0;
        vBand = self.eigenValues[0];vBandNumber = 0;
        fermi = self.fermiEnergy;
        occ = np.mean(self.occupations, axis = 1);

        for i, eig in enumerate(self.eigenValues):
            eig = eig - self.fermiEnergy;
            color = 'b';
            #print (i,occ[i],np.min(eig), np.max(eig));
            if (occ[i] >=self.occu) and (np.max(eig) > np.max(vBand)):
                vBand = eig;
                vBandNumber = i;
            elif (occ[i] < self.occu ) and (np.min(eig) < np.min(cBand)):
                cBand = eig;
                cBandNumber = i;
                #print (occ[i], i);

        maxValue = np.max(self.eigenValues);
        minValue = np.min(self.eigenValues);
        cLoc = [np.argmin(cBand), np.min(cBand)];
        vLoc = [np.argmax(vBand), np.max(vBand)];
        directBandTollerance = 2;
        self.bandGap = np.min(cBand) - np.max(vBand);
        self.directBandGap = (np.abs(cLoc[0] - vLoc[0]) < directBandTollerance);
        self.semiConductorType = 'None';
        #check the type of the semiconductor;
        if (self.bandGap > 0) and (self.bandGap < 9):
            if (np.abs(np.min(cBand))<np.abs(np.max(vBand))) or (cutZero == cBandNumber):
                self.semiConductorType = "n-Type";
            elif (np.abs(np.min(cBand)) >np.abs(np.max(vBand))) or (cutZero == vBandNumber):
                self.semiConductorType = "p-Type";
            elif (np.abs(np.abs(np.min(cBand))) <0.01 ):
                self.semiConductorType = "Inherent-Type";
        elif(self.bandGap > 9):
            self.semiConductorType = "Insulator";
        else:
            self.semiConductorType = "Metal";
        
        self.valuesForPlotting = [maxValue, minValue, vBand, cBand,vLoc, cLoc];

    def plotBand(self , usingAntonate = True, usingLines = True, usingFermiLine = True, usingXTicks = True):
        maxValue, minValue, vBand, cBand,vLoc, cLoc = self.valuesForPlotting;
        for i in self.eigenValues:
            color = 'black'; linewidth = 0.5; label = "";
            i = i - self.fermiEnergy;
            if (i == vBand).all(): color = 'green';linewidth = 1;label = "Valance band";
            if (i == cBand).all(): color = 'blue';linewidth = 1; label = "conductivity band";
            plt.plot(i,color=color, marker = '.', linewidth = linewidth, markersize = 2, label = label);
        
        #drawing fermi line at zero
        xValues = np.arange(0,self.nKPoints);
        if(usingFermiLine):
            fermiLine = xValues*0;
            plt.plot([0,self.nKPoints-1],[0,0], color = 'red', label = "Reference Line", linewidth = 0.5, linestyle = "--", alpha = 0.5 );

        #drawing the min and max value lines
        if (usingLines):
            vLine = np.arange(minValue,maxValue,0.01);
            plt.plot(vLine*0+vLoc[0],vLine,color = 'y');
            if(self.directBandGap == False): plt.plot(vLine*0+cLoc[0], vLine, color = 'y');
        #expresing plot limits
        plt.xlim(xmax = self.nKPoints-1, xmin = 0);
        #ymin, ymax = self.yLim + self.bandGap;
        ymin, ymax = self.yLim;
        self.yLim = [ymin, ymax];
        plt.ylim(ymin = self.yLim[0], ymax = self.yLim[1]);
        plt.ylabel("E-Ef(eV)"); plt.xlabel ('K Points');
        

        if (usingXTicks):
            ticks = [1]; tickLabels = [1];
            tickLabels = self.tickLabels;
            if(len(self.tickLocations) == len(self.tickLabels)):
                ticks = self.tickLocations;
            else:
                ticks = np.linspace(0,self.nKPoints-1,num = len(tickLabels));
            

            
            #print ("ticks:\t", ticks, tickLabels);
            plt.xticks(ticks, tickLabels);
            


        #show the band gap:
        if (self.bandGap > 0) and (usingAntonate):
            plt.annotate("", xy=(cLoc[0],vLoc[1]), xytext=(cLoc[0],cLoc[1]), arrowprops=dict(arrowstyle="|-|"))
            antX = 0;
            if (cLoc[0] + 4 > self.nKPoints-1):
                antX = cLoc[0] - 4;
            else: antX = cLoc[0] + 0.5;
            plt.annotate("{0:.3f} eV".format(self.bandGap), xy = (antX, (cLoc[1]+vLoc[1])/2), va='center', size=9);

        #plt.legend(loc = 0, fancybox = True, shadow = False,  ncol = 3, fontsize = 7);
        plt.grid(True);
        plt.show();

    def bondsCalculator(self):
        names = self.atoms.get_chemical_symbols();
        numbers = self.atoms.get_atomic_numbers();
        pos = self.atoms.get_positions();
        bonds = [];
        radius = 1.1;
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                b1 = radius*covalent_radii[numbers[i]];
                b2 = radius*covalent_radii[numbers[j]];
                pos1 = pos[i];
                pos2 = pos[j];
                distance = sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2 + (pos1[2] - pos2[2]) ** 2);
                print (b1+b2,distance, numbers[i]);
                if (distance <= (b1 + b2)):
                    bonds.append([names[i], names[j], i, j, distance]);

        self.bonds = np.array(bonds);
        #print (self.bonds);
        uniqueAtoms = np.unique(self.bonds[:,0]);
        self.staticsDatas = [];
        for at in uniqueAtoms:
            for bt in uniqueAtoms:
                temp = self.bonds[(self.bonds[:,0]==at) & (self.bonds[:,1]==bt)];
                if (len(temp)>0):
                    dists = [float(a) for a in temp[:,4]];

                    self.staticsDatas.append([at,bt,np.mean(dists),np.var(dists),np.std(dists),np.min(dists),np.max(dists), len(dists)]);
        dists = [float(a) for a in self.bonds[:,4]];
        self.staticsDatas.append(["ALL", len(dists), np.mean(dists), np.var(dists), np.std(dists), np.min(dists), np.max(dists),len(dists)]);
        #print(self.staticsDatas);

    def __str__(self):
        """this method is used for printing the class"""
        from collections import Counter;
        text =  "Number of Atoms: " + str(self.numberOfAtoms) + "\n";#adding number of atoms
        atomCounter = Counter(self.atoms.get_chemical_symbols());
        self.atomLabels = "";
        for key,val in atomCounter.items():
            self.atomLabels += "{}({}) ".format(key,val);
        text = text + "Atoms: {}\n".format(self.atomLabels);
        text = text + "Total Energy: {:2.3f} eV\n".format(self.totalEnergy);#adding total energy
        text = text + "Type: " + str(self.semiConductorType) + "\n";#adding type of material (semiconductor, ...)
        text = text + "Fermi Energy: {:2.3f} eV\n".format(self.fermiEnergy);#adding fermi energy
        if (self.semiConductorType != "Insulator" and self.semiConductorType !="Metal"):#adding Bandgap if the structure is semiconductor
            text = text + "BandGap: {:2.3f} eV\n".format(self.bandGap);
            text = text + "Direct BandGap: " + str(self.directBandGap) + "\n";
        minBond = self.bonds[np.argmin(self.bonds[:,4])];
        maxBond = self.bonds[np.argmax(self.bonds[:,4])];
        text = text + "Minimum bond Length :\n {}-{} atoms number: {}-{} distance:{:2.3f} ang\n".format(minBond[0],minBond[1],minBond[2],minBond[3],float(minBond[4]));
        text = text + "Maximum bond Length :\n {}-{} atoms number: {}-{} distance:{:2.3f} ang\n".format(maxBond[0], maxBond[1], maxBond[2],
                                                                          maxBond[3], float(maxBond[4]));
        print (self.staticsDatas);
        text = text + "means bond length: {:2.4f}\nstd of bond length: {:2.4f}".format(
            self.staticsDatas[-1][2],self.staticsDatas[-2][4]
        )
        return text;

    #Using the code in https://github.com/ghevcoul/coordinateTransform/blob/master/coordinateTransform.py;
    #With thanks to ghevcoul. 
    def frac2cart(self, cellParam, fracCoords):
        i = fracCoords;
        xPos = i[1]*cellParam[0][0] + i[2]*cellParam[1][0] + i[3]*cellParam[2][0]
        yPos = i[1]*cellParam[0][1] + i[2]*cellParam[1][1] + i[3]*cellParam[2][1]
        zPos = i[1]*cellParam[0][2] + i[2]*cellParam[1][2] + i[3]*cellParam[2][2]
        return [i[0], xPos, yPos, zPos]   #return values in shape of [symbol, x, y , z];


    def cart2frac(self, cellParam, cartCoords):
        latCnt = np.transpose(cellParam);
        from numpy.linalg import det;
        detLatCnt = det(latCnt)
        i = cartCoords;
        aPos = (det([[i[0], latCnt[0][1], latCnt[0][2]], [i[1], latCnt[1][1], latCnt[1][2]], [i[2], latCnt[2][1], latCnt[2][2]]])) / detLatCnt
        bPos = (det([[latCnt[0][0], i[0], latCnt[0][2]], [latCnt[1][0], i[1], latCnt[1][2]], [latCnt[2][0], i[2], latCnt[2][2]]])) / detLatCnt
        cPos = (det([[latCnt[0][0], latCnt[0][1], i[0]], [latCnt[1][0], latCnt[1][1], i[1]], [latCnt[2][0], latCnt[2][1], i[2]]])) / detLatCnt 
        return [ aPos, bPos, cPos];

    @staticmethod    
    def dosPlotter( a = 1, b = 0.02, filePath = "dos.dos", fermi = 0, yLim = [-1,1], usingTicks = True, usingGrid = True):
        with open(filePath) as f:
            firstLine = f.readline()
        fermi = float(firstLine.split()[-2]);
        dosDF = pd.read_csv(filePath, skiprows=1, sep=r"\s+", names = ['E','dos','intDos']);
        b, a = butter(a,b)
        x = dosDF['E'].astype(float)
        dos = (dosDF['dos']-fermi).astype(float)
        dosFiltered = filtfilt(b, a, dos , padlen=1)
        plt.plot(dosFiltered, x,'blue', label = "DOS");
        #draw zero line:
        plt.plot([0,np.max(dosFiltered + 10)], [0,0], 'black', linestyle = "--", linewidth = 0.5, alpha = 0.5);
        plt.ylim(yLim)
        plt.xlim (0,np.max(dosFiltered+10));
        print (usingTicks);
        if (usingTicks==False):
            plt.xticks([]);
            plt.yticks([]);
        plt.grid(usingGrid);
        plt.xlabel('DOS');
        plt.show()
        return [x,dosFiltered]

    def saveOutput(self,outputFile = "output.dat"):  ##saving output data into a file
        if outputFile == "output.dat":
            outputFile =self.directory + "/" +  outputFile;
        pos, posFrac = self.getCoordinates();
        text = str(self);
        text += "*******cartesian structure*******\n";
        for i in range(len(pos)):
            text += "{} \t{:2.6f}\t{:2.6f}\t{:2.6f}\n".format(pos[i][0],float(pos[i][1]),float(pos[i][2]),float(pos[i][3]));
        text += "\n\n*******fractional coordinates*******\n" ;
        for atom in posFrac:
            text += "{} \t{:2.6f}\t{:2.6f}\t{:2.6f}\n".format(atom[0],float(atom[1]),float(atom[2]),float(atom[3]));

        text += "\n\n*******cell vectors*******\n";
        for cell in self.cell:
            text += "{:2.6f}\t{:2.6f}\t{:2.6f}\n".format(float(cell[0]),float(cell[1]),float(cell[2]));
        text += "\n\n*******Bond Lengths*******\nsymbols\tindexes\tdistance\n";
        for bond in self.bonds:
            text += "{}-{}\t{}-{}\t{:2.4f}\n".format(bond[0],bond[1],bond[2],bond[3],float(bond[4]));
        text += "\n\n********Statistics of Bond lengths********\nbond\tmean\tstd  \tmin\tmax\tnum\n";
        for st in self.staticsDatas:
            text +="{}-{}\t{:2.4f}\t{:2.4f}\t{:2.4f}\t{:2.4f}\t{}\n".format(
                st[0],st[1],st[2],st[4],st[5],st[6],str(st[7])
            );
        with open(outputFile, "w") as text_file:
            text_file.write(text);


    def getCoordinates(self):
        names = self.atoms.get_chemical_symbols();
        numbers = self.atoms.get_atomic_numbers();
        pos = self.atoms.get_positions().tolist();
        posFrac = self.atoms.get_scaled_positions().tolist();
        for i in range(len(names)):
            pos[i] = [names[i]]+pos[i];
            posFrac[i] = [names[i]] + posFrac[i];
        return pos, posFrac;
    def view(self):
        view(self.atoms);
class Constants:
    def __init__(self):
        self.ang2au = 1.8897261339213;
        self.au2ang = 1./ang2au;
        self.h2ev = 27.2114;
        self.ry2ev = 13.6056980659;

ang2au = 1.8897261339213;
au2ang = 1./ang2au;
h2ev = 27.2114;

class Espresso:
    def __init__(self, file):
        self.file = file;
        self.directory  = os.path.dirname(os.path.realpath(__file__));
    def start(self):

        occ = 1;
        
        output = outputResults(fileName= self.file,path = os.path.dirname(os.path.abspath(self.file)), occu = occ );
        try:
            occ = int(input("If You want to change occupation number, you can enter it"));
        except:
            occ = 1;

        output.calculation();


        print ("\nOutput values:\n",output);
        ans = input("Do you want to save the structures in a file? (type the file name or only N to answer No)\n")
        if (ans.lower()!="n"):
            output.saveOutput(ans);
        ans = input("Do you want to plot the band structure? (Y for yes, others for No)\n")
        if (ans.lower()=="y"):     
            output.plotBand(usingLines = False);
        ans = input("Do you have a DOS file to plot? (Y for yes, others for No)\n");
        if (ans.lower()=="y") : output.dosPlotter();
        ans = input("Do you want to visualize the structure? (Y for yes, others for No)\n");
        if (ans.lower()=="y") : output.view();

if __name__ == '__main__':        
    repeat = True;
    directory = os.path.dirname(os.path.realpath(__file__));
    while(repeat):
        root = tk.Tk()
        root.withdraw();
        filePath = filedialog.askopenfilename(initialdir = directory,title = "Select a QE XML file to parse");
        directory = os.path.dirname(os.path.abspath(filePath));
        #print(type(filePath), filePath);
        root.destroy();
        if (str(filePath).lower().endswith(".xml")):
            espresso = Espresso(filePath);
            espresso.start();
            ans = input("Do you want to choose another XML file? (Y for yes, others for no)");
            if (ans.lower() != 'y'): 
                repeat = False;
        elif (str(filePath) == ""):
            repeat = False;
        else:
            print ("Wrong File Choosed");
