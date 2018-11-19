# QETools
QETools is a set of tools with gui to make it easier to posproccesing and preprocceisng the quantum espresso calculations.

At this time, it can extract the values from the quantum espresso xml file and calculate the bandgap and plot it, find bonds and their length and give a quick statistics on them (save them in output files after the other properties), plot dos files, create input files from structure file (CONTCAR,POSCAR,CIF) and define the parameters in the GUI. 

For using it, just run "python Run.py". 

Then choose a xml file created by quantum espresso and use the tools for extracting and calculations. 

This script is depends on PYQT5 (https://pypi.org/project/PyQt5/) and ASE (https://wiki.fysik.dtu.dk/ase/) python packages. 

![Proccessing a XML file](https://raw.githubusercontent.com/aerezaee/QETools/master/Images/1.PNG)
![Calculating bandgap and plotting](https://raw.githubusercontent.com/aerezaee/QETools/master/Images/2.PNG)
![Create input files](https://raw.githubusercontent.com/aerezaee/QETools/master/Images/3.PNG)
