from PyQt5 import QtWidgets, uic
import sys
import mido
import time
import asyncio
from threading import Thread
import rtmidi

# global variables
outPort = []
inPort = []
Volume1 = [0,0,0,0,0]
Volume2 = [0,0,0,0,0]

from RhythmSection import *

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        
        uic.loadUi('Prototype 1/Prototype_1.ui', self)
        openPorts()
        print(mido.get_input_names())
        print(mido.get_output_names())
        initRhythmSection(outPort, inPort)

        self.Slider_1_1.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_1_2.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_1_3.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_1_4.valueChanged.connect(lambda : onLevelChanged(self))
        self.Slider_1_5.valueChanged.connect(lambda : onLevelChanged(self))
        

        self.Slider_tempo.valueChanged.connect(lambda : onDialChanged(self))
        self.Button_play.clicked.connect(lambda : onPlayClicked(self))
        self.Button_stop.clicked.connect(lambda : onStopClicked(self))
        self.Button_fillin.clicked.connect(lambda : onFillInClicked(self))
        self.Button_rhythmOff.clicked.connect(lambda : onRhythmOffToggled(self))
        self.Button_pause.clicked.connect(lambda : onPauseClicked(self))

        self.show()
        inPort[0].callback = inHandlerLevel1

    def closeEvent(self, event):
        closePorts()





################################################################################
################################################################################
################################################################################
################################################################################


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
    inPort.append(mido.open_input(inputPorts[0]))
    
    print("input ports opened", len(inPort))

    i = 0
    for j in [0,2,3]:
        outPort.append(mido.open_output(outputPorts[j]))
    
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
    global outPort
    global Volume1

    m = mido.Message.from_bytes(message.bytes())
    for i in range(len(Volume1)):
        m.channel = i + 1                   #Start at channel 2
        outPort[1].send(m)

def onLevelChanged(mainWin):
    msg = mido.Message.from_bytes([0xB0, 0x07, 0x00])       #Controller volume message

    Volume1[0] = mainWin.Slider_1_1.value()
    Volume1[1] = mainWin.Slider_1_2.value()
    Volume1[2] = mainWin.Slider_1_3.value()
    Volume1[3] = mainWin.Slider_1_4.value()
    Volume1[4] = mainWin.Slider_1_5.value()
    print(Volume1)
    for i in range(len(Volume1)):
        msg.value = Volume1[i]
        msg.channel = i + 1
        outPort[1].send(msg)



app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()