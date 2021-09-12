
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import mido

# global variables
voiceMap = []
outPort = []
inPort = []
levelMap = [0, 31, 63, 95, 127]


class reverbLevelCtrl:
    reverbLevel = 0
    msg = mido.Message.from_bytes([0xB0, 0x07, 0x00])
    
    def onRevChanged(self):
        global outPort

        self.reverbLevel = self.dial.value()
        port = 1  # control message port
        self.msg.channel = self.kb
        self.msg.value = self.reverbLevel
        outPort[port].send(self.msg)
        
    def __init__(self, mainWin, x, y, kb):
        self.kb = kb
        self.dial = QDial(mainWin.centralwidget)
        self.dial.setObjectName(u"Reverb"+str(self.kb))
        self.dial.setGeometry(QRect(x, y, 80, 80))
        self.dial.setMinimum(0)
        self.dial.setMaximum(127)
        self.dial.setValue(0)
        self.dial.valueChanged.connect(lambda: self.onRevChanged())

        self.label = QLabel(mainWin.centralwidget)
        self.label.setObjectName(u"label_revb"+str(self.kb))
        dx = (len("Reverb  ")//2)*8
        self.label.setText("Reverb "+str(kb+1))
        
        self.label.setGeometry(QRect(x+50-dx, y+80, (len("Reverb  ")+2)*8, 16))


class voiceLevelCtrl:
    voiceLevel = 0
    msg = mido.Message.from_bytes([0xB0, 0x07, 0x00])
    
    def onLevelChanged(self):
        global outPort, voiceMap, levelMap
        
        self.voiceLevel = self.slider.value()
        port = voiceMap[self.kb][self.index][0]
        self.msg.channel = voiceMap[self.kb][self.index][1]
        self.msg.value = levelMap[self.voiceLevel]
        outPort[port].send(self.msg)

    def __init__(self, mainWin, x, y, kb, index):
        global voiceMap
        
        self.kb = kb
        self.index = index
        self.slider = QSlider(mainWin.centralwidget)
        self.slider.setObjectName(u"KB_"+str(self.kb)+"_"+str(self.index))
        self.slider.setGeometry(QRect(x, y, 91, 111))
        self.slider.setMaximum(3)
        self.slider.setPageStep(1)
        self.slider.setOrientation(Qt.Vertical)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(1)
        self.slider.valueChanged.connect(lambda: self.onLevelChanged())

        self.label = QLabel(mainWin.centralwidget)
        self.label.setObjectName(u"label_"+str(self.kb)+"_"+str(self.index))
        instrument = voiceMap[self.kb][self.index][2]
        dx = (len(instrument)//2)*8
        self.label.setText(instrument)
        
        self.label.setGeometry(QRect(x+45-dx, y-20, (len(instrument)+2)*8, 16))


def setupVoiceControllers(mainWin):
    x,y = 80,220
    mainWin.Voice = []
    for kb in range(len(voiceMap)):
        voiceList = []
        for i in range(4):
            voiceList.append(voiceLevelCtrl(mainWin, x+i*100, y+kb*170, kb, i))
            voiceList[i].onLevelChanged()   # reset to 0
        mainWin.Voice.append(voiceList)

def setupReverbControllers(mainWin):
    global voiceMap
    
    x,y = 500,200
    mainWin.Reverb = []
    for kb in range(len(voiceMap)):
        mainWin.Reverb.append(reverbLevelCtrl(mainWin, x, y+kb*170, kb))

def setVoiceMap():
    global voiceMap
    
    voiceMap = [[(0,0,"String"),(0,1,"Brass"),(0,2,"Flute"),(0,3,"Synth")],
                [(0,4,"Strings"),(0,5,"Brass"),(0,6,"Bass"),(0,7,"Plucked")]]

def initVoiceSection(mainWin, mainOutPorts, mainInPorts):
    global outPort, inPort
    
    outPort = mainOutPorts
    inPort = mainInPorts
    setVoiceMap()
    setupVoiceControllers(mainWin)
    setupReverbControllers(mainWin)

def inHandler(message):
    global outPort

    keyboard = message.channel
    port = voiceMap[keyboard][0][0]
    m = mido.Message.from_bytes(message.bytes())
    for i in range(len(voiceMap[keyboard])):
        m.channel = voiceMap[keyboard][i][1]
        m.velocity = m.velocity//2+64
        outPort[port].send(m)



