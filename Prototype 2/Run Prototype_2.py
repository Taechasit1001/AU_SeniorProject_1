from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QFile
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
import sys
import mido
from dataclasses import dataclass

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

masterVolume = 100
balanceVolume = 50
source1VolumeModifier = 1.0
source2VolumeModifier = 1.0
Transpose = 0
tempoValue = 100

profileArray = []
profileCurrent = 0

from RhythmSection import *

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        
        uic.loadUi('Prototype 2/Prototype_2.ui', self)

        print("Input :", mido.get_input_names())
        print("Output :", mido.get_output_names())

        #Theme
        themeFile="Prototype 2/ElegantDark.qss"
        with open(themeFile,"r") as theme:
            self.setStyleSheet(theme.read())


        #Configuration
        detectPorts()
        openPortsNew()
        initRhythmSection(level1OutPort, level1InPort)
        onLevelChanged(self)

        #Profile
        initProfile()
        loadProfile(self, 0)


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

        self.Slider_balance.valueChanged.connect(lambda : onVolumeChanged(self))
        self.Dial_volume.valueChanged.connect(lambda : onVolumeChanged(self))
        self.Button_volume_max.clicked.connect(lambda: volumeMax(self))
        self.Button_volume_mute.clicked.connect(lambda: volumeMute(self))
        self.Button_balance_both.clicked.connect(lambda: balanceBoth(self))
        self.Button_balance_first.clicked.connect(lambda: balanceFirst(self))
        self.Button_balance_second.clicked.connect(lambda: balanceSecond(self))

        self.Button_transpose_Reset.clicked.connect(lambda: transposeReset(self))
        self.Button_transpose_Plus.clicked.connect(lambda: transposeIncrease(self))
        self.Button_transpose_Minus.clicked.connect(lambda: transposeDecrease(self))

        self.Button_tempo_p15.clicked.connect(lambda: tempoIn1(self))
        self.Button_tempo_p20.clicked.connect(lambda: tempoIn2(self))
        self.Button_tempo_m15.clicked.connect(lambda: tempoDe1(self))
        self.Button_tempo_m20.clicked.connect(lambda: tempoDe2(self))

        self.Button_setting.clicked.connect(self.onOpenIO)

        self.Button_preset_1.clicked.connect(lambda: loadProfile(self, 0))
        self.Button_preset_2.clicked.connect(lambda: loadProfile(self, 1))
        self.Button_preset_3.clicked.connect(lambda: loadProfile(self, 2))
        self.Button_preset_4.clicked.connect(lambda: loadProfile(self, 3))
        self.Button_preset_5.clicked.connect(lambda: loadProfile(self, 4))
        self.Button_preset_6.clicked.connect(lambda: loadProfile(self, 5))
        self.Button_preset_Save.clicked.connect(lambda: saveProfile(self, profileCurrent))
        
        self.Browse_intro.clicked.connect(lambda: openIntro(self))
        self.Browse_base.clicked.connect(lambda: openBase(self))
        self.Browse_fillin.clicked.connect(lambda: openFillin(self))
        
        #Drum generator linkage
        self.Slider_tempo.valueChanged.connect(lambda : onDialChanged(self))
        self.Button_play.clicked.connect(lambda : onPlayClicked(self))
        self.Button_stop.clicked.connect(lambda : onStopClicked(self))
        self.Button_fillin.clicked.connect(lambda : onFillInClicked(self))
        self.Button_rhythmOff.clicked.connect(lambda : onRhythmOffToggled(self))
        self.Button_pause.clicked.connect(lambda : onPauseClicked(self))

        self.show()
        

    def closeEvent(self, event):
         closePortsNew()

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

@dataclass
class volume:
    source1: int
    source2: int
    balance: int
    master: int

    def __post_init__(self):
        if self.source1 is None:
            self.source1 = [0,0,0,0,0]
        if self.source2 is None:
            self.source2 = [0,0,0,0,0]
        if self.balance is None:
            self.balance = 50
        if self.master is None:
            self.master = 100

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

def closePortsNew():
    if level1InPort != None:
        level1InPort.callback = None
        level1InPort.close()
        level1OutPort.close()
        print("Level 1 Ports closed")
       
    if level2InPort != None:
        level2InPort.callback = None
        level2InPort.close()
        level2OutPort.close()
        print("Level 2 Ports closed")

def inHandlerLevel1(message):
    global level1OutPort
    global Volume1

    m = mido.Message.from_bytes(message.bytes())
    for i in range(len(Volume1)):
        m.channel = i + 1                   #Start at channel 2
        m.note += Transpose
        level1OutPort.send(m)

def inHandlerLevel2(message):
    global level2OutPort
    global Volume2

    m = mido.Message.from_bytes(message.bytes())
    for i in range(len(Volume2)):
        m.channel = i + 1                   #Start at channel 2
        m.note += Transpose
        level2OutPort.send(m)

def onLevelChanged(mainWin):
    msg = mido.Message.from_bytes([0xB0, 0x07, 0x00])       #Controller volume message

    Volume1[0] = mainWin.Slider_1_1.value()
    Volume1[1] = mainWin.Slider_1_2.value()
    Volume1[2] = mainWin.Slider_1_3.value()
    Volume1[3] = mainWin.Slider_1_4.value()
    Volume1[4] = mainWin.Slider_1_5.value()
    #print("Volume 1: ", Volume1)

    Volume2[0] = mainWin.Slider_2_1.value()
    Volume2[1] = mainWin.Slider_2_2.value()
    Volume2[2] = mainWin.Slider_2_3.value()
    Volume2[3] = mainWin.Slider_2_4.value()
    Volume2[4] = mainWin.Slider_2_5.value()
    #print("Volume 2: ", Volume2)
    
    for i in range(len(Volume1)):

        msg.value = int(Volume1[i] * source1VolumeModifier)
        msg.channel = i + 1
        level1OutPort.send(msg)

    for i in range(len(Volume2)):
        msg.value = int(Volume2[i] * source2VolumeModifier)
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

    openPortsNew()

def onVolumeChanged(mainWin):
    global masterVolume
    global balanceVolume
    global source1VolumeModifier
    global source2VolumeModifier

    masterVolume = mainWin.Dial_volume.value()
    balanceVolume = mainWin.Slider_balance.value()

    if balanceVolume == 50:
        source1VolumeModifier = masterVolume/100
        source2VolumeModifier = masterVolume/100
    elif balanceVolume < 50:
        source1VolumeModifier = masterVolume/100
        source2VolumeModifier = ((balanceVolume)/50) * masterVolume/100
    elif balanceVolume > 50:
        source1VolumeModifier = (abs(balanceVolume-100)/50) * masterVolume/100
        source2VolumeModifier = masterVolume/100

    onLevelChanged(mainWin)
    
    #Debug
    # print("Master: " + str(masterVolume))
    # print("Balance: " + str(balanceVolume))
    # print("Source 1: " + str(source1VolumeModifier))
    # print("Source 2: " + str(source2VolumeModifier))

def volumeMax(mainWin):
    global masterVolume
    masterVolume = 100
    mainWin.Dial_volume.setValue(100)
    onVolumeChanged(mainWin)

def volumeMute(mainWin):
    global masterVolume
    masterVolume = 0
    mainWin.Dial_volume.setValue(0)
    onVolumeChanged(mainWin)

def balanceBoth(mainWin):
    global balanceVolume
    balanceVolume = 50
    mainWin.Slider_balance.setValue(50)
    onVolumeChanged(mainWin)

def balanceFirst(mainWin):
    global balanceVolume
    balanceVolume = 0
    mainWin.Slider_balance.setValue(0)
    onVolumeChanged(mainWin)

def balanceSecond(mainWin):
    global balanceVolume
    balanceVolume = 100
    mainWin.Slider_balance.setValue(100)
    onVolumeChanged(mainWin)

def transposeIncrease(mainWin):
    global Transpose
    if Transpose < 11:
        Transpose += 1
    mainWin.lcdNumber_transpose.display(Transpose)

def transposeDecrease(mainWin):
    global Transpose
    if Transpose > -11:
        Transpose -= 1
    mainWin.lcdNumber_transpose.display(Transpose)

def transposeReset(mainWin):
    global Transpose
    Transpose = 0
    mainWin.lcdNumber_transpose.display(Transpose)

def tempoIn1(mainWin):
    global tempoValue
    if mainWin.Slider_tempo.value()*1.5 <= 200:
        tempoValue = mainWin.Slider_tempo.value()*1.5
        mainWin.Slider_tempo.setValue(mainWin.Slider_tempo.value()*1.5)
    elif mainWin.Slider_tempo.value()*1.5 > 200:
        tempoValue = 200
        mainWin.Slider_tempo.setValue(200)

def tempoIn2(mainWin):
    global tempoValue
    if mainWin.Slider_tempo.value()*2 <= 200:
        tempoValue = mainWin.Slider_tempo.value()*2
        mainWin.Slider_tempo.setValue(mainWin.Slider_tempo.value()*2)
    elif mainWin.Slider_tempo.value()*2 > 200:
        tempoValue = 200
        mainWin.Slider_tempo.setValue(200)

def tempoDe1(mainWin):
    global tempoValue
    if mainWin.Slider_tempo.value()/1.5 >= 1:
        tempoValue = mainWin.Slider_tempo.value()/1.5
        mainWin.Slider_tempo.setValue(mainWin.Slider_tempo.value()/1.5)
    elif mainWin.Slider_tempo.value()/1.5 < 1:
        tempoValue = 1
        mainWin.Slider_tempo.setValue(1)

def tempoDe2(mainWin):
    global tempoValue
    if mainWin.Slider_tempo.value()/2 >= 1:
        tempoValue = mainWin.Slider_tempo.value()/2
        mainWin.Slider_tempo.setValue(mainWin.Slider_tempo.value()/2)
    elif mainWin.Slider_tempo.value()/2 < 1:
        tempoValue = 1
        mainWin.Slider_tempo.setValue(1)

def initProfile():
    for i in range(6):
        Profile = volume(None, None, None, None)
        profileArray.append(Profile)

    # profileArray[0] = volume([10,10,10,10,10],None,10,20)
    # profileArray[1] = volume(None,None,44,55)
    # print(profileArray[0])
    # print(profileArray[1])

def saveProfile(mainWin, index: int):
    profileArray[index].source1[0] = mainWin.Slider_1_1.value()
    profileArray[index].source1[1] = mainWin.Slider_1_2.value()
    profileArray[index].source1[2] = mainWin.Slider_1_3.value()
    profileArray[index].source1[3] = mainWin.Slider_1_4.value()
    profileArray[index].source1[4] = mainWin.Slider_1_5.value()
    profileArray[index].source2[0] = mainWin.Slider_2_1.value()
    profileArray[index].source2[1] = mainWin.Slider_2_2.value()
    profileArray[index].source2[2] = mainWin.Slider_2_3.value()
    profileArray[index].source2[3] = mainWin.Slider_2_4.value()
    profileArray[index].source2[4] = mainWin.Slider_2_5.value()
    profileArray[index].balance =mainWin.Slider_balance.value()
    profileArray[index].master = mainWin.Dial_volume.value()

def loadProfile(mainWin, index: int):
    global profileCurrent
    profileCurrent = index
    mainWin.Slider_1_1.setValue(profileArray[index].source1[0])
    mainWin.Slider_1_2.setValue(profileArray[index].source1[1])
    mainWin.Slider_1_3.setValue(profileArray[index].source1[2])
    mainWin.Slider_1_4.setValue(profileArray[index].source1[3])
    mainWin.Slider_1_5.setValue(profileArray[index].source1[4])
    mainWin.Slider_2_1.setValue(profileArray[index].source2[0])
    mainWin.Slider_2_2.setValue(profileArray[index].source2[1])
    mainWin.Slider_2_3.setValue(profileArray[index].source2[2])
    mainWin.Slider_2_4.setValue(profileArray[index].source2[3])
    mainWin.Slider_2_5.setValue(profileArray[index].source2[4])
    mainWin.Slider_balance.setValue(profileArray[index].balance)
    mainWin.Dial_volume.setValue(profileArray[index].master)
    onVolumeChanged(mainWin)

    if index == 0:
        mainWin.Button_preset_1.setChecked(True)
        mainWin.Button_preset_2.setChecked(False)
        mainWin.Button_preset_3.setChecked(False)
        mainWin.Button_preset_4.setChecked(False)
        mainWin.Button_preset_5.setChecked(False)
        mainWin.Button_preset_6.setChecked(False)
    elif index == 1:
        mainWin.Button_preset_1.setChecked(False)
        mainWin.Button_preset_2.setChecked(True)
        mainWin.Button_preset_3.setChecked(False)
        mainWin.Button_preset_4.setChecked(False)
        mainWin.Button_preset_5.setChecked(False)
        mainWin.Button_preset_6.setChecked(False)
    elif index == 2:
        mainWin.Button_preset_1.setChecked(False)
        mainWin.Button_preset_2.setChecked(False)
        mainWin.Button_preset_3.setChecked(True)
        mainWin.Button_preset_4.setChecked(False)
        mainWin.Button_preset_5.setChecked(False)
        mainWin.Button_preset_6.setChecked(False)
    elif index == 3:
        mainWin.Button_preset_1.setChecked(False)
        mainWin.Button_preset_2.setChecked(False)
        mainWin.Button_preset_3.setChecked(False)
        mainWin.Button_preset_4.setChecked(True)
        mainWin.Button_preset_5.setChecked(False)
        mainWin.Button_preset_6.setChecked(False)
    elif index == 4:
        mainWin.Button_preset_1.setChecked(False)
        mainWin.Button_preset_2.setChecked(False)
        mainWin.Button_preset_3.setChecked(False)
        mainWin.Button_preset_4.setChecked(False)
        mainWin.Button_preset_5.setChecked(True)
        mainWin.Button_preset_6.setChecked(False)
    elif index == 5:
        mainWin.Button_preset_1.setChecked(False)
        mainWin.Button_preset_2.setChecked(False)
        mainWin.Button_preset_3.setChecked(False)
        mainWin.Button_preset_4.setChecked(False)
        mainWin.Button_preset_5.setChecked(False)
        mainWin.Button_preset_6.setChecked(True)

def openIntro(mainWin):
    intro = QFileDialog.getOpenFileName(None, 'Open Intro MIDI file')
    if intro:
        mainWin.Edit_intro.setText(intro[0])

def openBase(mainWin):
    base = QFileDialog.getOpenFileName(None, 'Open Base MIDI file')
    if base:
        mainWin.Edit_base.setText(base[0])

def openFillin(mainWin):
    fill = QFileDialog.getOpenFileName(None, 'Open Fill-in MIDI file')
    if fill:
        mainWin.Edit_fillin.setText(fill[0])
    



app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()




##########################################################################################
################################# Deplicated Functions ###################################
##########################################################################################
def inHandlerTP(message):
    global outPort

    port = 1
    m = mido.Message.from_bytes(message.bytes())
    m.channel = 1
    m.note += 12
    outPort[port].send(m) 

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