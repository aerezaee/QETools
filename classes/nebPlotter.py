import numpy as np
import matplotlib.pyplot as plt
import os
"""Usage:
nebPlot = nebPlotter("1\n2\n5\n4\n","\n");
nebPlot.plot();
"""
class nebPlotter():
    def __init__(self,energyText ="1\n2\n3\n4\n",locationText = "1\n2\n3\n4\n", sep = "\n" ):
        self.energies = np.fromstring(energyText,dtype = float, sep = sep);
        self.locations = np.fromstring(locationText,dtype = float, sep = sep);
        self.minValue = 0;
        self.minValueIndex = 1;
        self.energiesDiff = np.array((0,0));
        self.maxLocations = list();
        self.yRange = np.array((0,0));
        self.xRange = np.array((0,0));
        self.calc();
    def calc(self):
        self.minValue = np.min(self.energies);
        self.minValueIndex = np.argmin(self.energies)+1;
        self.energiesDiff = self.energies - self.minValue;
        for i, value in enumerate(self.energiesDiff):
            if i > 0 and i < len(self.energiesDiff) - 1:
                if value > self.energiesDiff[i - 1] and value > self.energiesDiff[i + 1]:
                    self.maxLocations.append([i + 1, value]);
    def plot(self,xUnit = "\AA", yUnit="eV"):
        energiesDiff = self.energiesDiff;
        from scipy.interpolate import CubicSpline
        x = self.locations;
        print(x);
        bci = CubicSpline(x, energiesDiff, extrapolate=False)
        xNew = np.linspace(min(x), max(x), 1000)
        yNew = bci(xNew)
        plt.scatter(x, energiesDiff);
        plt.plot(xNew, yNew, linewidth=0.3, color='green');
        plt.annotate("", xy=(self.minValueIndex - 0.5, -0.2), xytext=(self.minValueIndex + 0.5, -0.2),
                     arrowprops=dict(arrowstyle="-"))  # for arrow
        for point in self.maxLocations:
            plt.annotate("", xy=(point[0], 0), xytext=(point[0], point[1]), color="blue",
                         arrowprops=dict(arrowstyle="<|-|>", color='red'))  # for arrow
            plt.annotate("{0:.2f} eV".format(point[1]), xy=(point[0] + 0.1, point[1] / 2), va='center',
                         size=9);  # for text
        plt.ylim(bottom=0);
        plt.xlim(left=0, right= x[-1] );
        plt.grid(True);
        plt.ylabel("Energy (${}$)".format(yUnit),fontsize = 14);
        plt.xlabel(r"Migration Path (${}$)".format(xUnit), fontsize = 14);
        plt.show();
    def __str__(self):
        text = "Energy Diff:\n";
        for energy in self.energiesDiff:
            text += "{:2.4f}\n".format(energy);
        text += "\nmax activation energy:\n{:2.4f}\n".format(np.max(self.energiesDiff));
        text += "max activation energy location:\n{:2.4f}\n".format(np.argmax(self.energiesDiff)+1);
        return text;




