from PyQt5 import QtWidgets, uic
import sys
import mido
import time
import asyncio
from threading import Thread
import rtmidi

# global variables
outPort = []
outPortName = []
outPortNameFull = []
inPort = []
inPortName = []
inPortNameFull = []

Volume1 = [0,0,0,0,0]
level1InPort = None
level1OutPort = None
level1IndexIn = 0
level1IndexOut = 3

Volume2 = [0,0,0,0,0]
level2InPort = None
level2OutPort = None
level2IndexIn = 1
level2IndexOut = 4

from RhythmSection import *

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        
        uic.loadUi('Prototype 2/Prototype_2.ui', self)

        print("Input :", mido.get_input_names())
        print()
        print("Output :", mido.get_output_names())

        

        #Configuration
        detectPorts()
        openPortsNew()
        initRhythmSection(level1OutPort, level1InPort)
        onLevelChanged(self)




        #Other linkage
        self.Slider_1_1.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_1_2.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_1_3.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_1_4.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_1_5.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_2_1.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_2_2.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_2_3.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_2_4.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_2_5.valueChanged.connect(lambda : onLevelChanged(self))
        self.Button_setting.clicked.connect(self.onOpenIO)

        
        
        #Drum generator linkage
        self.Slider_tempo.valueChanged.connect(lambda : onDialChanged(self))
        self.Button_play.clicked.connect(lambda : onPlayClicked(self))
        self.Button_stop.clicked.connect(lambda : onStopClicked(self))
        self.Button_fillin.clicked.connect(lambda : onFillInClicked(self))
        self.Button_rhythmOff.clicked.connect(lambda : onRhythmOffToggled(self))
        self.Button_pause.clicked.connect(lambda : onPauseClicked(self))

        self.show()
        

    #def closeEvent(self, event):
    #    closePorts()

    def onOpenIO(self):
        self.ioWindow = ioUI()
        self.ioWindow.show()

#################################################################################

class ioUI(QtWidgets.QMainWindow, QtWidgets.QPushButton):
    def __init__(self):
        super(ioUI,self).__init__()
        uic.loadUi('Prototype 2/Prototype_2_io.ui', self)

        self.comboBox_Source1_i.addItems(inPortNameFull)
        self.comboBox_Source1_i.setCurrentIndex(level1IndexIn)
        self.comboBox_Source1_i.currentTextChanged.connect(lambda : onIndexChanged(self))

        self.comboBox_Source1_o.addItems(outPortNameFull)
        self.comboBox_Source1_o.setCurrentIndex(level1IndexOut)
        self.comboBox_Source1_o.currentTextChanged.connect(lambda : onIndexChanged(self))

        self.comboBox_Source2_i.addItems(inPortNameFull)
        self.comboBox_Source2_i.setCurrentIndex(level2IndexIn)
        self.comboBox_Source2_i.currentTextChanged.connect(lambda : onIndexChanged(self))

        self.comboBox_Source2_o.addItems(outPortNameFull)
        self.comboBox_Source2_o.setCurrentIndex(level2IndexOut)
        self.comboBox_Source2_o.currentTextChanged.connect(lambda : onIndexChanged(self))



################################################################################
################################################################################
################################################################################
################################################################################

def detectPorts():
    global inPortNameFull
    global outPortNameFull
    inPortNameFull = mido.get_input_names()
    outPortNameFull = mido.get_output_names()

def openPortsNew():
    global level1InPort
    global level1OutPort
    global level2InPort
    global level2OutPort
    global inPortNameFull
    global outPortNameFull

    if level1InPort != None:
        level1InPort.callback = None
        level1InPort.close()
        level1OutPort.close()
       
    if level2InPort != None:
        level2InPort.callback = None
        level2InPort.close()
        level2OutPort.close()
        

    level1InPort = mido.open_input(inPortNameFull[level1IndexIn])
    level1OutPort = mido.open_output(outPortNameFull[level1IndexOut])
    level2InPort = mido.open_input(inPortNameFull[level2IndexIn])
    level2OutPort = mido.open_output(outPortNameFull[level2IndexOut])

    level1InPort.callback = inHandlerLevel1
    level2InPort.callback = inHandlerLevel2


def openPorts():
    global outPort, inPort

    inputPorts = mido.get_input_names()
    outputPorts = mido.get_output_names()
    
    i = 0
    #for i in range(len(inputPorts)):
    #    inPort.append(mido.open_input(inputPorts[1]))
    #     if inputPorts[i][:4] == "Micr":
    #         inPort.append(mido.open_input(inputPorts[i]))
    # for j in range(len(inPort)):
    #    inPort[j].callback = inHandler
    for j in [0,1]:
        inPort.append(mido.open_input(inputPorts[j]))
        inPortName.append(inputPorts[j])
    print("input ports opened", len(inPort))


    i = 0
    for j in [0,3,4]:
        outPort.append(mido.open_output(outputPorts[j]))
        outPortName.append(outputPorts[j])
    print("Output ports opened", len(outPort))
    
def closePorts():
    global outPort, inPort
    
    while outPort != []:
        outPort[len(outPort)-1].close()
        del outPort[len(outPort)-1]
    while inPort != []:
        inPort[len(inPort)-1].close()
        del inPort[len(inPort)-1]

    print("Port closed")

def inHandlerTP(message):
    global outPort

    port = 1
    m = mido.Message.from_bytes(message.bytes())
    m.channel = 1
    m.note += 12
    outPort[port].send(m) 

def inHandlerLevel1(message):
    global level1OutPort
    global Volume1

    m = mido.Message.from_bytes(message.bytes())
    for i in range(len(Volume1)):
        m.channel = i + 1                   #Start at channel 2
        level1OutPort.send(m)

def inHandlerLevel2(message):
    global level2OutPort
    global Volume2

    m = mido.Message.from_bytes(message.bytes())
    for i in range(len(Volume2)):
        m.channel = i + 1                   #Start at channel 2
        level2OutPort.send(m)

def onLevelChanged(mainWin):
    msg = mido.Message.from_bytes([0xB0, 0x07, 0x00])       #Controller volume message

    Volume1[0] = mainWin.Slider_1_1.value()
    Volume1[1] = mainWin.Slider_1_2.value()
    Volume1[2] = mainWin.Slider_1_3.value()
    Volume1[3] = mainWin.Slider_1_4.value()
    Volume1[4] = mainWin.Slider_1_5.value()
    print("Volume 1: ", Volume1)

    Volume2[0] = mainWin.Slider_2_1.value()
    Volume2[1] = mainWin.Slider_2_2.value()
    Volume2[2] = mainWin.Slider_2_3.value()
    Volume2[3] = mainWin.Slider_2_4.value()
    Volume2[4] = mainWin.Slider_2_5.value()
    print("Volume 2: ", Volume2)
    
    for i in range(len(Volume1)):
        msg.value = Volume1[i]
        msg.channel = i + 1
        level1OutPort.send(msg)

    for i in range(len(Volume2)):
        msg.value = Volume2[i]
        msg.channel = i + 1
        level2OutPort.send(msg)

def onIndexChanged(mainWin):
    global level1IndexIn
    global level1IndexOut
    global level2IndexIn
    global level2IndexOut

    level1IndexIn = mainWin.comboBox_Source1_i.currentIndex()
    level1IndexOut = mainWin.comboBox_Source1_o.currentIndex()
    level2IndexIn = mainWin.comboBox_Source2_i.currentIndex()
    level2IndexOut = mainWin.comboBox_Source2_o.currentIndex()
    print("Current index is " + str(level1IndexOut))

    openPortsNew()





app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()