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
from RhythmSection import *

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        
        uic.loadUi('Test 4/Draft 4.ui', self)
        openPorts()
        print(mido.get_input_names())
        print(mido.get_output_names())
        initRhythmSection(outPort, inPort)

        self.button = self.findChild(QtWidgets.QPushButton, 'Button_source1_1')
        self.button.clicked.connect(self.FirstButtonPressed)

        self.button2 = self.findChild(QtWidgets.QPushButton, 'Button_source1_2')
        self.button2.clicked.connect(self.SecondButton)

        self.button3 = self.findChild(QtWidgets.QPushButton, 'Button_source1_3')
        self.button3.clicked.connect(self.ThirdButton)

        self.button4 = self.findChild(QtWidgets.QPushButton, 'Button_source1_4')
        #self.button4.clicked.connect(self.FourthButton)

        self.buttonPlay = self.findChild(QtWidgets.QPushButton, "Button_play")
        #self.buttonPlay.clicked.connect(self.PlayMidi)

        self.Slider_tempo.valueChanged.connect(lambda : onDialChanged(self))
        self.Button_play.clicked.connect(lambda : onPlayClicked(self))
        self.Button_transpose_Reset.clicked.connect(lambda : onStopClicked(self))
        self.Button_stop.clicked.connect(lambda : onFillInClicked(self))
        self.Button_outro.clicked.connect(lambda : onRhythmOffToggled(self))
        self.Button_pause.clicked.connect(lambda : onPauseClicked(self))

        self.show()

    def closeEvent(self, event):
        closePorts()

    def FirstButtonPressed(self):
        inPort[0].callback = inHandler

    def SecondButton(self):
        inPort[0].callback = None

    def ThirdButton(self):
        inPort[0].callback = inHandlerTP



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

def inHandler(message):
    global outPort

    port = 1
    m = mido.Message.from_bytes(message.bytes())
    m.channel = 1
    outPort[port].send(m)

def inHandlerTP(message):
    global outPort

    port = 1
    m = mido.Message.from_bytes(message.bytes())
    m.channel = 1
    m.note += 12
    outPort[port].send(m)    



app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()