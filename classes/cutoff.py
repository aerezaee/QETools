from subprocess import Popen, PIPE
import numpy as num



class QeRun:
    def __init__(self,inputFile = "test.in",changeValue = "ecutwfc"):
        self.inputText = open(inputFile).read();
        self.energies = [];
        self.cutoff = [];
        self.currentCutOff = 0;
        self.changeValue = changeValue;
        self.psFolder = "";
        self.toChange = "";


        for line in self.inputText.splitlines():
            if self.changeValue in line:
                self.toChange = line;
            if "pseudo_dir" in line:
                self.psFolder = line;
                print(self.psFolder);
        
        self.inputText = self.inputText.replace(self.psFolder,"pseudo_dir = './inputs/ps/'");

    def getEnergy(self,output):
        try:
            for line in output.decode("utf-8").splitlines():
                if "!    total energy              =" in line:
                    words = line.split();
                    print(words[4]);
                    self.energies.append(float(words[4]));
                    self.cutoff.append(float(self.currentCutOff));
            print(self.energies,self.cutoff);
        except Exception as e:
            print("error");
            print(str(e));

    
    
    def run(self,inputChanged,runCommand = ["wsl","pw.x"]):
        byteInput = str.encode(inputChanged);
        #process = Popen(["wsl pw.exe"],stdout=PIPE,stdin=PIPE);
        process = Popen(runCommand,stdout=PIPE,stdin=PIPE);
        (output,err) = process.communicate(input = byteInput);
        exitCode = process.wait();
        self.getEnergy(output);    
    
    
    def inputMaker(self,steps = [1,10,20],runCommand = ["wsl","pw.x"]):
        for i in steps:
            change = str(self.changeValue) + " = " + str(i);
            self.inputChanged = self.inputText.replace(self.toChange,change);
            self.currentCutOff = i;
            self.run(self.inputChanged,runCommand=runCommand);
            outputFile = open("output","w");
            outputFile.write(self.inputChanged);
            outputFile.close();


if __name__ == "__main__":
    qr = QeRun();
    qr.inputMaker();
