
from auditok import ADSFactory, AudioEnergyValidator, StreamTokenizer, player_for, from_file
import pyaudio
import wave
import sys
import time
import random
import glob, os
import platform
import speech_recognition as sr
import asyncio
import _thread
import os.path
import json
import uuid
import datetime

try: 
   # DEFAULT VALUES
   energy_threshold = 65
   duration = 5000 # seconds
   FORMAT = pyaudio.paInt16
   CHANNELS = 2
   RATE = 48000
   sample_rate = RATE
   CHUNK = 1024
   chunk = CHUNK
   RECORD_SECONDS = 5000

   DATA_FILE_PATH = 'data.json'

   if len(sys.argv) > 1:
     energy_threshold = float(sys.argv[1])

   if len(sys.argv) > 2:
     duration = float(sys.argv[2])

   # set up audio source  
   asource = ADSFactory.ads(record=True, max_time = duration)

   #check os system and set sample rate 48000 for Linux (Raspberry Pi)
   _os = platform.system()
   print(_os)
   if (_os == 'Darwin') or (_os == 'Windows'): # macOs
      sample_rate = asource.get_sampling_rate()
   
   sample_width = asource.get_sample_width()
   channels = asource.get_channels()

   print(sample_width, sample_rate)
   
   validator = AudioEnergyValidator(sample_width=sample_width, energy_threshold = energy_threshold)
   tokenizer = StreamTokenizer(validator=validator, min_length=80, max_length=RECORD_SECONDS, max_continuous_silence=400, mode = StreamTokenizer.DROP_TRAILING_SILENCE) #  

   p = pyaudio.PyAudio()

   def init():
      if os.path.exists('data.json'): 
         setDataFile()      
      else:
         createDataFile()
      asource.open()
      print("\n  ** Make some noise (dur:{}, energy:{})...".format(duration, energy_threshold))
      tokenizer.tokenize(asource, callback=savefile)
      asource.close() 

   def createDataFile():
      # check if file exists      
      with open(DATA_FILE_PATH) as f:
         json.dump([], f)   

   def setDataFile():     
      with open(DATA_FILE_PATH, 'rb') as f:     
         try:
            data = json.load(f)
            print('file ok', data)
         except:            
            print('unable to open file')            

   def test(params, aloha):
      print(params, aloha)
      print('thread started')
      time.sleep(1)
      print('threaded')

   def thread(func, params = [None, None]):
      try:
         _thread.start_new_thread( func, (params[0], params[1]) )
      except:
         print("error starting thread")

   def savefile(data, start, end):      
      # thread(test, [1, 2])
      print('-----------------------')
      print("Acoustic activity at: {0}--{1}".format(start, end))  
      filename = "teste_{0}_{1}.wav".format(start, end)
      waveFile = wave.open(filename, 'wb')
      waveFile.setnchannels(channels)
      waveFile.setsampwidth(sample_width)
      waveFile.setframerate(sample_rate)
      waveFile.writeframes(b''.join(data))
      waveFile.close()
      # salvar arquivo como data no data.json   
      saveToData(filename, start, end)

      # play next file
      playfile(filename)            

   def saveToData(filename, start, end):
      # calculate length in milsec 1s = 100
      length = end - start
      # get timestamp 
      timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
      # start process of analyzing audio ... (async)
      # thread(analyze_audio, [filename, None])
      audio_data = {
                     "filename": filename,
                     "timestamp": timestamp,
                     "length": length,
                     "text": "",
                     "tags": []           
                  }

      data = []
      with open(DATA_FILE_PATH,"rb") as f:
         data = json.load(f)
      
      with open(DATA_FILE_PATH,"w") as f:         
         data.append(audio_data)
         json.dump(data, f, indent=4, sort_keys=True)
         print(data)

   def analyze_audio(filename, _ = "_"):      
      r = sr.Recognizer("ru")
      print("reading file", filename)
      with sr.WavFile(filename) as source:              # use "test.wav" as the audio source
          audio = r.record(source)                        # extract audio data from the file
      try:
          print("Transcription: " + r.recognize(audio))   # recognize speech using Google Speech Recognition
      except LookupError:                                 # speech is unintelligible
          print("Could not understand audio")  
    
   def getAudioToPlay(filename):
      return filename

   def playfile(filename):       
      asource.close()
      print('input muted')
      # get random file from folder
      # filename = random.choice(glob.glob("*.wav"))
      wave_player = wave.open(filename, 'rb')
      data = wave_player.readframes(chunk)
      # open stream to play audio 
      stream = p.open(
            format = FORMAT,
            channels = channels,
            rate = sample_rate,
            output = True)
      print('playing: ' + filename)      
      # read all file     
      while len(data) > 0:
            stream.write(data)
            data = wave_player.readframes(chunk)
      else:          
         stream.close()
         wave_player.close()
         print('input unmuted')
         asource.open()
         print('-----------------------')      
   
   init()

except KeyboardInterrupt:

   asource.close()
   sys.exit(0)

except Exception as e:
   
   sys.stderr.write(str(e) + "\n")
   sys.exit(1)
                               
      
      

