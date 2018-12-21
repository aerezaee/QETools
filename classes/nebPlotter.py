import numpy as np
import matplotlib.pyplot as plt
import os
"""Usage:
nebPlot = nebPlotter("1\n2\n5\n4\n","\n");
nebPlot.plot();
"""
class nebPlotter():
    def __init__(self,energyText ="5\n2\n10\n4\n",locationText = "1\n2\n3\n4\n", sep = "\n" , highestArrow = True, label = "Path 1"):
        self.energies = np.fromstring(energyText,dtype = float, sep = sep);
        self.locations = np.fromstring(locationText,dtype = float, sep = sep);
        self.label = label;
        self.minValue = 0;
        self.minValueIndex = 1;
        self.energiesDiff = np.array((0,0));
        self.maxLocations = list();
        self.minLocations = list();
        self.allLocations = list();
        self.yRange = np.array((0,0));
        self.xRange = np.array((0,0));
        self.highestArrow = highestArrow;
        self.calc();
    def calc(self):
        self.minValue = np.min(self.energies);
        self.minValueIndex = np.argmin(self.energies)+1;
        self.energiesDiff = self.energies - self.minValue;
        for i, value in enumerate(self.energiesDiff):
            if i > 0 and i < len(self.energiesDiff) - 1:
                if value > self.energiesDiff[i - 1] and value > self.energiesDiff[i + 1]:
                    self.maxLocations.append([self.locations[i], value]);
                if value <self.energiesDiff[i-1] and value < self.energiesDiff[i+1]:
                    self.minLocations.append([self.locations[i],value]);
            elif i == 0:
                if value > self.energiesDiff[i+1]:
                    self.maxLocations.append([self.locations[i], value]);
                if value < self.energiesDiff[i+1]:
                    self.minLocations.append([self.locations[i], value]);
            else:
                if value > self.energiesDiff[i-1]:
                    self.maxLocations.append([self.locations[i], value]);
                if value  < self.energiesDiff[i-1]:
                    self.minLocations.append([self.locations[i], value]);

        for i,x in enumerate(self.maxLocations):#Finding the Minimums
            diff = 10000000;
            index = 0;
            value = list();
            for j,y in enumerate(self.minLocations):
                if (j >= len(self.minLocations)-1):#for the last point
                    if (x[0] > self.minLocations[j][0]):
                        value = self.minLocations[j];
                    break;
                print(x[0]< self.minLocations[j + 1][0],x[1] > self.minLocations[j][0],x ,self.minLocations[j][0]);
                if (x[0] < self.minLocations[j + 1][0] and x[0] > self.minLocations[j][0]):
                    if (self.minLocations[j + 1][1] > self.minLocations[j][1]):
                        value = self.minLocations[j];
                        print (j,j+1);
                        break;
                    else:
                        value = self.minLocations[j + 1];
                elif (x[0] < self.minLocations[j][0]):
                    value = self.minLocations[j];
                    break;
                elif (x[0] > self.minLocations[j][0]):
                    value = self.minLocations[j];


            self.allLocations.append([x[0],value[0],x[1],value[1],x[1]-value[1]]);
        print (self.allLocations);
    def plot(self,xUnit = "\AA", yUnit="eV", label = "Path"):
        energiesDiff = self.energiesDiff;
        #Drawing curves between points by interpollating
        from scipy.interpolate import CubicSpline,interp1d,PchipInterpolator,Akima1DInterpolator,KroghInterpolator
        x = self.locations;
        #bci = CubicSpline(x, energiesDiff, extrapolate=True)
        #bci = PchipInterpolator(x,energiesDiff);
        bci = interp1d(x, energiesDiff, kind = "quadratic");
        xNew = np.linspace(min(x), max(x), 1000)
        yNew = bci(xNew)

        plt.plot(xNew, yNew, linewidth=0.5, color='green');#plotting the curves
        plt.scatter(x, energiesDiff,label = self.label,linewidths = 2,color = "blue");#plotting the points

        plt.annotate("", xy=(self.minValueIndex - 0.5, -0.2), xytext=(self.minValueIndex + 0.5, -0.2),
                     arrowprops=dict(arrowstyle="-"))  #Drawing the minimum line
        if self.highestArrow == False:
            for point in self.allLocations:#Drawing the arrows and minimum lines
                print ("Point:",point);
                plt.annotate("", xy=(point[0], point[2]), xytext=(point[0], point[3]), color="blue",
                             arrowprops=dict(arrowstyle="<|-|>", color='magenta', lw = 0.7))  # for arrow
                plt.annotate("", xy=(point[0] + (point[0]-point[1])/5, point[3]), xytext=(point[1], point[3]), color="blue",
                             arrowprops=dict(arrowstyle="-", color='black', lw=0.7))  # for arrow
                if point[0] == x[0]:
                    plt.annotate("{:.2f}".format(point[2]-point[3]), xy=(point[0] +0.2, point[2] / 2), va='center',
                                 size=12, rotation = 90);  # for text
                else:
                    plt.annotate("{:.2f}".format(point[2]-point[3]), xy=(point[0] - 0.5, (point[2]+point[3]) / 2), va='center',
                                 size=12, rotation = 90);  # for text
        else:
            point = 0;
            index = np.argmax(np.array(self.maxLocations)[:,1]);#finding the maximum value
            point = [self.maxLocations[index][0],self.maxLocations[index][1]];
            print("Point:", point);
            plt.annotate("", xy=(point[0], point[2]), xytext=(point[0], point[3]), color="blue",
                         arrowprops=dict(arrowstyle="<|-|>", color='red', lw=0.7))  # for arrow
            plt.annotate("", xy=(point[0] - 0.5, point[3]), xytext=(point[0] + 0.5, point[3]), color="blue",
                         arrowprops=dict(arrowstyle="-", color='red', lw=0.7))  # for arrow
            if point[0] == x[0]:
                plt.annotate("{:.2f} ${}$".format(point[2] - point[3], yUnit), xy=(point[0] + 0.2, point[2] / 2),
                             va='center',
                             size=12, rotation=90);  # for text
            else:
                plt.annotate("{:.2f} ${}$".format(point[2] - point[3], yUnit),
                             xy=(point[0] - 0.5, (point[2] + point[3]) / 2), va='center',
                             size=12, rotation=90);  # for text

        plt.ylim(bottom=-(np.max(energiesDiff)/10));
        plt.xlim(left=np.max(x)/(-20), right= x[-1]+np.max(x)/(20) );
        plt.xticks(self.locations);
        plt.grid(False);
        plt.legend(fontsize = "large");
        plt.ylabel("Energy (${}$)".format(yUnit),fontsize = 14);
        plt.xlabel(r"Migration Path (${}$)".format(xUnit), fontsize = 14);
        plt.show();
    def __str__(self):
        text = "Energy Diff:\n";
        activationEnergies = list();
        for energy in self.allLocations:
            text += "{:2.4f}\n".format(energy[4]);
            activationEnergies.append(energy[4]);

        text += "\nmax activation energy:\n{:2.4f}\n".format(np.max(activationEnergies));
        return text;




