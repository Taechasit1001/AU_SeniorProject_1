
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import mido

# global variables
voiceMap = []
outPort = []
inPort = []
levelMap = [0, 31, 63, 95, 127]

class voiceLevelCtrl:
    voiceLevel = 0
    msg = mido.Message.from_bytes([0xB0, 0x07, 0x00])
    
    def onLevelChanged(self):
        global outPort, voiceMap, levelMap
        
        print(self.kb, self.index+1, self.slider.value())
        self.voiceLevel = self.slider.value()
        port = voiceMap[self.kb][self.index][0]
        self.msg.channel = voiceMap[self.kb][self.index][1]
        self.msg.value = levelMap[self.voiceLevel]
        outPort[port].send(self.msg)

    def __init__(self, mainWin, x, y, kb, index):
        self.kb = kb
        self.index = index
        self.slider = QSlider(mainWin.centralwidget)
        self.slider.setObjectName(u"Upper_1")
        self.slider.setGeometry(QRect(x, y, 91, 111))
        self.slider.setMaximum(3)
        self.slider.setPageStep(1)
        self.slider.setOrientation(Qt.Vertical)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(1)
        self.onLevelChanged()   # reset to 0
        self.slider.valueChanged.connect(lambda: self.onLevelChanged())

def setupVoiceControllers(mainWin):
    x,y = 80,220
    mainWin.Voice = []
    for kb in range(2):
        voiceList = []
        for i in range(4):
            voiceList.append(voiceLevelCtrl(mainWin, x+i*100, y+kb*170, kb, i))
        mainWin.Voice.append(voiceList)

def setVoiceMap():
    global voiceMap
    
    voiceMap = [[(0,0),(0,1),(0,2),(0,3)], [(0,4),(0,5),(0,6),(0,7)]]

def initVoiceSection(mainWin, mainOutPorts, mainInPorts):
    global outPort, inPort
    
    outPort = mainOutPorts
    inPort = mainInPorts
    setVoiceMap()
    setupVoiceControllers(mainWin)

def inHandler(message):
    global outPort

    keyboard = message.channel
    port = voiceMap[keyboard][0][0]
    m = mido.Message.from_bytes(message.bytes())
    for i in range(len(voiceMap[keyboard])):
        m.channel = voiceMap[keyboard][i][1]
        outPort[port].send(m)



