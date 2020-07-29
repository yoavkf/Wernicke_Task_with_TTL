# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pyaudio
import wave
from pathlib import Path
import pandas as pd
from pynput.keyboard import Key, Listener, KeyCode
import numpy as np
import time
from datetime import datetime

# import tkinter
# from ctypes import windll
from IO64class import IO64
import csv
import configparser
"""
bin codes: (10 bit words)
all ones (1024) - task initiation 
1:499 - prompt number 
512 - continue
513 - repeat
514 - pause
515 - esc
"""
# %%


def read_configuration():
    config = configparser.ConfigParser()
    config.read("Wernica_config.ini")
    params = {"Speaker":    int(config["DEFAULT"]["Speaker"]),
              "Microphone": int(config["DEFAULT"]["Microphone"]),
              "start_in_trial": int(config["DEFAULT"]["start_in_trial"])}
    return params


def on_press(key):

    global kill
    global wait
    global repeat
    global pause
    global digIO
    if key == Key.right or key == Key.page_down:
        wait = False
        pause = False
        digIO.sendDigitalWord(512)
    if key == Key.esc:
        kill = True
        digIO.sendDigitalWord(515)

    if key == Key.left or key == Key.page_up:
        repeat = True
        wait = False
        digIO.sendDigitalWord(513)

    if key == KeyCode.from_char('b'):
        pause = not pause
        digIO.sendDigitalWord(514)


if __name__ == "__main__":
    params = read_configuration()
    digIO = IO64()

    ###################### AUDIO OUTPUT ########################
    p = pyaudio.PyAudio()
    if params["Speaker"] == -1 or params["Microphone"] == -1:
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            print("Device ID#", i, " : ",
                  p.get_device_info_by_host_api_device_index(0, i).get('name'))
        print(' ')
        microphone_index = int(input('Microphone Device ID No:'))
        speaker_index = int(input('Speaker Device ID No:'))
    else:
        microphone_index = params["Microphone"]
        speaker_index = params["Speaker"]

    chunk = 1024

    microphone_channels = p.get_device_info_by_index(microphone_index)[
        'maxInputChannels']
    microphone_rate = int(p.get_device_info_by_index(
        microphone_index)['defaultSampleRate'])
    microphone_format = pyaudio.paInt32

    ###################### PROMPTS ########################
    p_prompt = pyaudio.PyAudio()

    prompt_stream = p_prompt.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=24000,
                                  output=True,
                                  output_device_index=speaker_index)
    # Start the prompt stream
    print('\tStarting prompt stream')
    prompt_stream.start_stream()

    ###################### KEYPRESS LISTENER ###################
    kill = False
    wait = False
    repeat = False
    pause = False

    listener = Listener(on_press=on_press)
    listener.start()

    #################### LOAD PROMPTS #######################
    prompts = pd.read_excel('prompt_order.xlsx',
                            sheet_name='prompts', header=None)
    prompts = prompts[0].tolist()
    prompts = [str(x).zfill(4) + '.wav' for x in prompts]

    questions = pd.read_excel(
        'prompt_order.xlsx', sheet_name='questions', header=None)
    questions = questions[0].tolist()
    questions = [str(x).zfill(4) + '.wav' for x in questions]

    ################### INITIALIZE COUNTER ###################
    counter = params["start_in_trial"] - 1
    if counter < 0:
        counter = 0
    digIO.sendDigitalWord(counter)
    # %% [markdown]
    # ## Play Sentences

    ################### LOG file ###################
    folder = 'log'
    log_name = "wernickeLOG_" + datetime.now().strftime("%m_%d_%Y_%H_%M")+'.csv'
    csvfile = open(Path(folder, log_name), "w", newline='')
    log = csv.writer(csvfile)
    rows = ["trial", "prompt", "time"]
    log.writerow(rows)
    # %%
    kill = False
    # initiate:
    pause = True
    print('Press "right" to start task')
    while pause:
        time.sleep(0.1)

    while counter < len(prompts) and not kill:

        while pause:
            time.sleep(0.1)

        prompt = prompts[counter]
        print(prompt)

        # Load prompt
        pathname = 'prompts'
        wf = wave.open(str(Path(pathname, prompt)), 'rb')

        # Play prompt
        print(counter + 1)
        digIO.sendDigitalWord(counter+1)  # excel numbering starts in 1
        digIO.sendDigitalWord(0)  # excel numbering starts in 1
        digIO.sendDigitalWord(int(prompt[:-4]))  # excel numbering starts in 1

        prompt_start_time = datetime.now().strftime("%H_%M_%S_%f")
        data = wf.readframes(chunk)
        while len(data) > 0:

            prompt_stream.write(data)
            data = wf.readframes(chunk)

        wf.close()
        digIO.sendDigitalWord(0)
        # log:
        rows = [counter + 1, prompt, prompt_start_time]
        log.writerow(rows)

        # Pause
        if prompt == '0481.wav' or prompt == '0482.wav' or prompt == 'repeat.wav' or prompt == 'lastword.wav' or prompt in questions:
            wait = True
            while wait:
                time.sleep(0.1)
        else:
            time.sleep(0.3)

        if repeat:
            repeat = False
        else:
            counter += 1

    # %% [markdown]
    # ## Close Streams

    # %%
    ##################### CLOSE STREAMS ######################
    listener.stop()
    csvfile.close()
    prompt_stream.close()
    p_prompt.terminate()

    # %%
