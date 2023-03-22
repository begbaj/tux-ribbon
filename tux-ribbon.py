#!/bin/python3
import curses
import random
import time
from curses import wrapper
from aubio import source, onset
import os
import threading
from pygame import mixer

CURRENT_SEL = None
CURRENT_VIEW = None

############
# views
############

def play(main_window,status_window,stdscr):
    file_path = "demos/music-sounds-better-with-you.mp3"
    window_size = 2048 # FFT size
    hop_size = window_size // 1
    sample_rate = 0
    src_func = source(file_path, sample_rate, hop_size)
    sample_rate = src_func.samplerate
    onset_func = onset('energy', window_size, hop_size)
    duration = float(src_func.duration) / src_func.samplerate
    keys = ['d','f','j','k']
    onset_times = []

    while True: # read frames
        samples, num_frames_read = src_func()
        if onset_func(samples):
            onset_time = onset_func.get_last_s()
            if onset_time < duration:
                onset_times.append([onset_time, keys[int((onset_time*1000)%4)], 0])
            else:
                break
        if num_frames_read < hop_size:
            break
    for i in onset_times:
        if random.choice([True,False]):
            onset_times.remove(i)
    time_begin = time.time()
    mixer.init()
    mixer.music.load(file_path)
    mixer.music.play()
    stdscr.nodelay(True)
    last_key = ""
    is_paused = False
    scrsize = stdscr.getmaxyx()
    beat_window = 3
    score = 0

    while True:
        try:
            key = stdscr.getkey()
        except: 
            key = ""
        current_time = mixer.music.get_pos()/1000
        if key != "":
            stdscr.clear()
            last_key = key
            if key == "q":
                break
            if key == "r":
                mixer.music.play()
            if key == "p":
                if is_paused:
                    mixer.music.unpause()
                    is_paused = False
                else:
                    is_paused = True
                    mixer.music.pause()
            if key in ['d','f','j','k']: 
                for beat in onset_times:
                    if beat[0] <= current_time + 0.050 and beat[0] >= current_time - 0.050 and key == beat[1] and beat[2] == 1:
                        score += 50
                        beat[2] = 2
        stdscr.addstr(10,0, f"key: {last_key}")
        scrsize = stdscr.getmaxyx()
        if current_time >= duration:
            break
        for i in range(0,scrsize[1]):
            stdscr.addch(int(scrsize[0]/2)-5,i,' ')
            for j in range(1,3):
                stdscr.addch(int(scrsize[0]/2)-j,i, " ")
                stdscr.addch(int(scrsize[0]/2)+j,i, " ")

            stdscr.addch(int(scrsize[0]/2), i, ' ')
        for i in range(-3,4):
            stdscr.addch(int(scrsize[0]/2)+i, int(scrsize[1]/2), "|", curses.color_pair(4))
        for beat in onset_times:
            if beat[0] > current_time - beat_window and beat[0] <= current_time + beat_window:
                color = curses.color_pair(1)
                if beat[0] <= current_time:
                    if beat[2] == 2:
                        color = curses.color_pair(3)
                    else:
                        color = curses.color_pair(1)
                        if beat[2] == 1:
                            beat[2] = -1
                            if score > 0:
                                #score -= 50
                                pass
                elif beat[0] < current_time + beat_window/5:
                    color = curses.color_pair(3)
                elif beat[0] < current_time + beat_window/2:
                    color = curses.color_pair(2)
                    beat[2] = 1
                    
                if beat[1] == 'd':
                    stdscr.addch(int(scrsize[0]/2)-2,int(((beat[0]-current_time+beat_window)/(beat_window*2))*scrsize[1]), "X", color)
                elif beat[1] == 'f':
                    stdscr.addch(int(scrsize[0]/2)-1,int(((beat[0]-current_time+beat_window)/(beat_window*2))*scrsize[1]), "X", color)
                elif beat[1] == 'j':
                    stdscr.addch(int(scrsize[0]/2)+1,int(((beat[0]-current_time+beat_window)/(beat_window*2))*scrsize[1]), "X", color)
                elif beat[1] == 'k':
                    stdscr.addch(int(scrsize[0]/2)+2,int(((beat[0]-current_time+beat_window)/(beat_window*2))*scrsize[1]), "X", color)
                stdscr.addch(int(scrsize[0]/2)-5,int(((beat[0]-current_time+beat_window)/(beat_window*2))*scrsize[1]), beat[1])

        stdscr.addstr(int(scrsize[0]/2)+5, int(scrsize[1]/2), f"{str(current_time).split('.')[0]}  -  {duration}")
        stdscr.addstr(int(scrsize[0]/2)+6, int(scrsize[1]/2), f"score: {score}")
        stdscr.refresh()
    mixer.music.stop()
    stdscr.nodelay(False)

def mapSelector():
    pass

def mapPlayer():
    pass

def mapEditor():
    pass

def settings(main_window,status_window,stdscr):
    global CURRENT_SEL
    global CURRENT_VIEW

    if CURRENT_SEL == None:
        CURRENT_SEL = 0

    # PRINTING STEP
    main_window.addstr(1,1,"Nothing here...")
    status_window.addstr(1,1,"press any key to return on main menu")
    
    # GET INPUT STEP
    try:
        key = stdscr.getkey()
    except:
        key = None
    if key != None:
        CURRENT_VIEW=mainMenu

def playMenu():
    pass

def editorMenu():
    pass

def mainMenu(main_window,status_window,stdscr):
    global CURRENT_SEL
    global CURRENT_VIEW

    if CURRENT_SEL == None:
        CURRENT_SEL = 0
        
    MAIN_MENU =[
        {
            "text":"Play",
            "desc":"Select a map to play"
        },

        {
            "text":"Edit",
            "desc":"Select a map to edit or make a new one"
        },

        {
            "text":"Settings",
            "desc":"Change game settings"
        },

        {
            "text":"Exit",
            "desc":"Quit Tux-Ribbon",
        },
    ]

    # PRINTING STEP
    for i in range(0,len(MAIN_MENU)):
        selection = " "
        if i == CURRENT_SEL:
            selection = ">"
            status_window.addstr(1,1, f'{MAIN_MENU[i]["desc"]}')
        main_window.addstr(i+1, 1, f'{selection}{MAIN_MENU[i]["text"]}')
        status_window.addstr(0,int(curses.COLS/2), f'Current selection {CURRENT_SEL}')
    
    # GET INPUT STEP
    try:
        key = stdscr.getkey()
    except:
        key = None

    if key == "KEY_DOWN":
        CURRENT_SEL = (CURRENT_SEL+1)%len(MAIN_MENU)
    elif key == "KEY_UP":
        CURRENT_SEL = (CURRENT_SEL-1)%len(MAIN_MENU)

    elif key == "\n":
        if CURRENT_SEL == 0:
            CURRENT_VIEW = play
        elif CURRENT_SEL == 1:
            pass
        elif CURRENT_SEL == 2:
            CURRENT_VIEW = settings
        elif CURRENT_SEL == 3:
            return -1


############
# functions
############

def _loadSettings():
    pass

def _scanMaps():
    pass

def _loadMap():
    pass

def _saveMap():
    pass


def main(stdscr):
    global CURRENT_SEL
    global CURRENT_VIEW

    # clear screen
    stdscr.clear()
    scrsize = stdscr.getmaxyx()

    # set default color palette
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_GREEN)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_WHITE)
    curses.curs_set(False)
    
    main_window = curses.newwin(curses.LINES-3, curses.COLS-6, 0, 3)
    status_window = curses.newwin(3, curses.COLS-6, curses.LINES-3, 3)
    stdscr.nodelay(True)

    CURRENT_VIEW = mainMenu

    while True:
        main_window.clear()
        status_window.clear()
        main_window.box()
        status_window.box()
        
        status = CURRENT_VIEW(main_window,status_window,stdscr)
        if status == -1:
            break
        # CLEAR SCREEN
        main_window.refresh()
        status_window.refresh()
        time.sleep(0.01)

wrapper(main) # does all the init process
