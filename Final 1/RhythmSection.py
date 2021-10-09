import mido
import threading
import time

# global variables

DRUMPORT = 0  # Loop MIDI Port 3 or IAC Driver Bus 3
tempo = 240   # but is actually 100
ticks_per_beat = 480
sec_per_beat = 60/tempo
sec_per_tick = sec_per_beat/ticks_per_beat

startInterval = 0
baseName = ''
introName = ''
fillInName = ''
msgList = []
baseEvents = []
introEvents = []
Events = None
fillInEvents = []
resolution = 60   # number of ticks for each 1/32nd
stopped = True
paused = False
rhythmOff = False

outPort = None
inPort = None
window = None

def initRhythmSection(mainOutPorts, mainInPorts):
    global outPort, inPort
    outPort = mainOutPorts
    inPort = mainInPorts

# event handlers

def onDialChanged(mainWin):
    global tempo, ticks_per_beat, sec_per_tick
    
    tempo = mainWin.Slider_tempo.value()
    mainWin.Edit_tempo.setText(str(tempo))

    tempo *= 2.4    # timing adjustment
    sec_per_beat = 60.0/tempo
    sec_per_tick = sec_per_beat/ticks_per_beat
    print(sec_per_tick, ": one beat in", sec_per_tick*480.0, "second")


def playEventList(interval):
    global outPort, sec_per_tick, resolution, stopped, paused, startInterval
    global baseEvents, introEvents, fillInEvents, Events

    if not rhythmOff:
        if not paused:
            if not stopped:
                threading.Timer(resolution*sec_per_tick, playEventList, \
                            [(interval+1)%len(Events)]).start()

            wrappedInterval = interval%len(Events)    
            thisEventList = Events[wrappedInterval]
            if Events == introEvents and wrappedInterval == len(introEvents)-1:
                Events = baseEvents
            if Events == fillInEvents and wrappedInterval == len(fillInEvents)-1:
                Events = baseEvents
            if thisEventList != []:
                for msg in thisEventList:
                    if msg.time == 0:
                        outPort.send(msg)
                    else: threading.Timer(msg.time*sec_per_tick, outPort.send, [msg]).start()
        else:
            startInterval = interval+1

def onPauseClicked(mainWin):
    global paused

    if mainWin.Button_pause.isChecked():
        paused = True
        # if playing Events,
        # this will cause playEventList to record next interval as startInterval
    else:
        paused = False
        if startInterval != 0:
            threading.Timer(0, playEventList, [startInterval]).start()
            
def onStopClicked(mainWin):
    global stopped, startInterval, paused
    
    stopped = True
    if paused:
        mainWin.Button_pause.toggle()
        onPauseClicked(mainWin)
    startInterval = 0

def onRhythmOffToggled(mainWin):
    global rhythmOff, stopped, paused, startInterval
    
    if mainWin.Button_rhythmOff.isChecked():
        rhythmOff = True
        onStopClicked(mainWin)
    else:
        rhythmOff = False


def loadMidiFile(midiFile):
    global resolution
    
    msgList = []
    tick = 0
    for i, track in enumerate(midiFile.tracks):
        for msg in track:
            if (not msg.is_meta) and msg.channel == 9:
                # convert time to absolute tick
                msg.time += tick
                msgList.append(msg)
                tick = msg.time

    # distribute msg into 1/32nd intervals     
    midiEvents = []
    tickList = []
    curInterval = 0
    for msg in msgList:
        assigned = False
        while not assigned:
            if (msg.time//resolution) == curInterval:
                msg.time -= curInterval*resolution
                tickList.append(msg)
                assigned = True
            else:
                midiEvents.append(tickList)
                tickList = []
                curInterval += 1
    midiEvents.append(tickList)
    curInterval += 1
    
    # fill up the last bar (assuming that the loop doesn't end on first beat
    while curInterval%32 != 0:
        midiEvents.append([])
        curInterval += 1

    return midiEvents

def onFillInClicked(mainWin):
    global fillInEvents, Events

    if len(fillInEvents) > 0:
        Events = fillInEvents


def onPlayClicked(mainWin):
    global outPort, msgList, resolution, stopped, paused, startInterval, rhythmOff, sec_per_tick
    global baseEvents, introEvents, fillInEvents, Events

    if not (rhythmOff or paused):
        if stopped:
            baseName = mainWin.Edit_base.text().strip()
            introName = mainWin.Edit_intro.text().strip()
            fillInName = mainWin.Edit_fillin.text().strip()
            print(baseName)
            print(introName)
            print(fillInName)

            if baseName != '':
                baseFile = mido.MidiFile(baseName)
                baseEvents = loadMidiFile(baseFile)
            else:
                baseEvents = []
                
            if introName != '':
                introFile = mido.MidiFile(introName)
                introEvents = loadMidiFile(introFile)
            else:
                introEvents = []
                
            if fillInName != '':
                fillInFile = mido.MidiFile(fillInName)
                fillInEvents = loadMidiFile(fillInFile)
            else:
                fillInEvents = []

            for eventList in [baseEvents, introEvents, fillInEvents]:
                print(len(eventList))
               
            stopped = False
            
            if len(introEvents) == 0:
                Events = baseEvents
            else:
                Events = introEvents

            '''
            debugger
            for curInterval in range(len(baseEvents)):
                print(curInterval,":",end="")
                for msg in baseEvents[curInterval]:
                    print(msg)
                    print(curInterval,":",end="")
                print("------")      
            '''
        
            threading.Timer(0, playEventList, [startInterval]).start()

    



