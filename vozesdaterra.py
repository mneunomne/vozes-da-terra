#!/usr/bin/python3 python3

from auditok import ADSFactory, AudioEnergyValidator, StreamTokenizer, player_for, from_file
import pyaudio
import wave
import sys
import time
import random
import glob, os
import platform
import speech_recognition as sr
from thread import *
from chaves import *
import uuid
import datetime 
import ftplib
import numpy as np
import memoria
from pydub import AudioSegment
import nltk    
from nltk import tokenize
from argparse import ArgumentParser
from operator import attrgetter

import json

import re

from gui import *

# sys.stdout = open('log.txt', 'w')

parser = ArgumentParser()

# settings - modos de configurar o auditok e dinâmica de reprodução:
# 
#  teste:
#     Escuta, grava, responde logo após com 1 áudio
#  
#  entrevista:
#     parâmetros para ambiente com pouco barulho, e intermissões não tão curtas
#     sem resposta, só escuta
#
#  ambiente:
#     
#
#  música
#

parser.add_argument("-s", "--settings", dest="settings",
                    help="Settings do auditok e dinâmica de reprodução", default="teste")
# sample rate
parser.add_argument("-r", "--sample_rate", dest="sample_rate",
                     default=48000, help="sample rate")

# threshhold de volume para iniciar gravação
parser.add_argument("-t", "--threshold", dest="threshold", 
                     default=52, help="energy threshold for auditok")

# modo debug
parser.add_argument("-D", "--DEBUG", dest="DEBUG", 
                     default=False, help="energy threshold for auditok")

# data file
parser.add_argument("-j", "--json_file_path", dest="data_file", 
                     default='data.json', help="destination data file")

# pasta para guardar arquivos gravados
parser.add_argument("-a", "--audio_folder", dest="audio_folder", 
                     default='pankararu/', help="local folder where files are saved")

# modos de funcionamento
parser.add_argument("-m", "--modo", dest="modo",
                    help="Modo de funcionamento", default="random")

args = parser.parse_args()

sample_rate = int(args.sample_rate)
FORMAT = pyaudio.paInt16
CHANNELS = 2
CHUNK = 1024
chunk = CHUNK
GUI = False

time_last_played = 0
last_played_type = " "

# parametros de áudio
max_length = 1000000
max_interval = 12000
max_continuous_silence = 500
min_length = 150

settings = args.settings
if settings == 'entrevista':
   max_length = 50000
   max_interval = 15000
   max_continuous_silence = 500
   min_length = 100

## JSON DATA FILE
data = []


# parametros de funcionamento
MODO = args.modo
DEBUG = args.DEBUG

SAVE_FILES = True
UPLOAD_TO_SERVER = False
TRANSCRIPTION = True

# local audio storage folder 
audio_folder = args.audio_folder

# parametros para bando de dados
SERVER_URL     = 'aurora.webfactional.com'
SERVER_PATH    = 'webapps/vozes_da_terra/data'
USERNAME       = 'aurora'
PASSWORD       = 'matrizes33'
DATA_FILE_PATH =  args.data_file

# parametros de áudio
energy_threshold = int(args.threshold)
FORMAT = pyaudio.paInt16
CHANNELS = 2
sample_rate = int(args.sample_rate)
CHUNK = 1024
chunk = CHUNK

print("sample_rate", sample_rate)
last_played_time = 0
try:
   last_played_time = 0  
   last_played_type = " "
   # set up audio source  
   asource = ADSFactory.ads(record=True, max_time = min_length, sampling_rate = sample_rate)

   #check os system and set sample rate 48000 for Linux (Raspberry Pi)
   _os = platform.system()
   if (_os == 'Darwin') or (_os == 'Windows'): # macOs
      sample_rate = asource.get_sampling_rate()
   
   # get sample width and channels from ads factory 
   sample_width = asource.get_sample_width()
   channels = asource.get_channels()
   
   # START VALIDATOR
   validator = AudioEnergyValidator(sample_width=sample_width, energy_threshold = energy_threshold)
   tokenizer = StreamTokenizer(validator=validator, min_length=min_length, max_length=max_length, max_continuous_silence=max_continuous_silence) #  

   # LOAD PYAUDIO 
   p = pyaudio.PyAudio()

   # start classe memoria
   _memoria = memoria.Memoria()

   # gui vars
   if GUI:
      root = Tk()
      display = GUI(root)

   if TRANSCRIPTION:
      # LOAD RECOGNIZER
      recognizer = sr.Recognizer(800, "pt-BR")     
      # nltk vars
      stop_words = nltk.corpus.stopwords.words('portuguese')
      stemmer = nltk.stem.RSLPStemmer()           

      path = os.getenv('PATH')
      print("Path is: %s" % (path,))
      print("shutil_which gives location: %s" % (sr.shutil_which('flac')))

   # print out sound devices
   if DEBUG:       
      print('sample rate',  sample_rate)      
      for i in range(p.get_device_count()):
         dev = p.get_device_info_by_index(i)
         print((i,dev['name'],dev['maxInputChannels']))   

   def init():
      last_played_time = time.time()
      # thread(timer, [last_played_time, 0])
      # timer(last_played_time, 0)

      if GUI:
         display.set_state('listening')
      
      if MODO == 'echo':
         ## abrir microfone
         asource.open()
         print("\n  ** Make some noise (dur:{}, energy:{})...".format(max_length, energy_threshold))      
         ## começar tokenizer
         tokenizer.tokenize(asource, callback=savefile)      
         asource.close()
      
      ### random player ###
      elif MODO == 'random':
         playrandom()

      ### ###
      elif MODO == 'oraculo':
         ## abrir o mic, pegar texto
        #  asource.open()
         print('modo', MODO)
         listen(0, 0)     



   def savefile(data, start, end):      
      print("Acoustic activity at: {0}--{1}".format(start, end))        

      filename = audio_folder + '{:%Y-%m-%d_%H:%M:%S}'.format(datetime.datetime.now())
      # filename = audio_folder + "teste_{0}_{1}.wav".format(start, end)      
      # create folder if 'audios' doesnt exist
      if not os.path.exists(os.path.dirname(filename)):
          try:
              os.makedirs(os.path.dirname(filename))
          except OSError as exc: # Guard against race condition
              if exc.errno != errno.EEXIST:
                  raise
      # save wav file
      waveFile = wave.open(filename, 'wb')
      waveFile.setnchannels(channels)
      waveFile.setsampwidth(sample_width)
      waveFile.setframerate(sample_rate)
      waveFile.writeframes(b''.join(data))
      waveFile.close()

      # normalize volume
      sound = AudioSegment.from_file(filename, "wav")
      normalized_sound = match_target_amplitude(sound, -15.0)

      with_fade = normalized_sound.fade_in(200).fade_out(200)

      with_fade.export(filename, format="wav")

      # salvar arquivo como data no data.json 
      audio_id = str(uuid.uuid4()) 
      saveToData(filename, start, end, audio_id)      
      # dependendo do MODO de funcionamento, 
      # diferentes comportamentos ocorrem 
      # ao novo áudio ser gravado. 
      onNewAudio(filename, audio_id)

   def saveToData(filename, start, end, audio_id):
      # calculate length in milsec 1s = 100
      length = end - start
      # get timestamp 
      timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())      
      # start process of analyzing audio ... (async)      
      if TRANSCRIPTION:
          thread(analyze_audio, [filename, audio_id])      
      # data structure
      audio_data = {
                     "id": audio_id,
                     "filename": filename,
                     "timestamp": timestamp,
                     "length": length,
                     "text": "",
                     "server_path": SERVER_URL + SERVER_PATH,
                     "stemms": [],
                     "last_played": timestamp,
                     "isUploaded": False
                  }         
      _memoria.append(audio_data)      
      # upload file to server
      if UPLOAD_TO_SERVER:
         thread(upload, [filename, audio_id])

   def listen(a, b):
      try:
         with sr.Microphone() as source:
            ## recognizer.adjust_for_ambient_noise(source, duration = 1)
            print("Started listening!")
            try:
               audio = recognizer.listen(source, 10)
            except TimeoutError: 
               print('time exceded')
               playrandom()
               return
      except:
         time.sleep(1)
         listen(0,0)
      try:
         print('-------------------')                   
         print('recognizing text...')

         text = recognizer.recognize(audio, show_all = False, timeout = None)

         print("Transcription: " + recognizer.recognize(audio))   # recognize speech using Google Speech Recognition         
         # playrandom()
         # time.sleep(1)

         wordList = re.sub("[^\w]", " ",  text.lower()).split()

         file = get_file_from_list(wordList)
         filename = file["filename"]         
         playfile(filename)

         #channel()
         listen(0, 0)
      except LookupError:                                 # speech is unintelligible
          print("Could not understand audio")                   
          #channel()
          listen(0, 0)
          # thread(listen, [0, 0])

   def analyze_audio(filename, audio_id):       
      # print("reading file", filename)
      with sr.WavFile(filename) as source:              # use "test.wav" as the audio source
          audio = recognizer.record(source)                        # extract audio data from the file
      try:
         print("Transcription: " + recognizer.recognize(audio))   # recognize speech using Google Speech Recognition         
         text = recognizer.recognize(audio)
         _memoria.set(audio_id, "text", text)
         # update cloud db
         _memoria.onFileUploaded(audio_id)
         thread(stemm_text, [text, audio_id])
      except LookupError:                                 # speech is unintelligible
          print("Could not understand audio")  

   def stemm_text(text, audio_id = -1):
      print('text', text)
      tokens = tokenize.word_tokenize(text, language='portuguese')    
      stemms = [stemmer.stem(i) for i in tokens if i not in stop_words]
      print('stemms', stemms)    
      if audio != -1:
         _memoria.set(audio_id, "stemms", stemms)      

   def upload(filename, audio_id):
      session = ftplib.FTP(SERVER_URL, USERNAME, PASSWORD)
      print('started ' + SERVER_URL + ' session' )      
      session.cwd(SERVER_PATH)
      file = open(filename,'rb')                       # file to send
      session.storbinary('STOR ' + audio_id + '.wav', file)     # send the file
      print('file saved in server')      
      _memoria.set(audio_id, "isUploaded", True)
      # close file and FTP
      file.close()
      session.quit()
      print('end session')


   def getAudioToPlay(filename):
      return filename

   def playfile(filename, audio_id = 0, file_channels = 1):    
      if GUI:
          display.set_state('playing')
      
      if MODO == 'echo':
         asource.close()      
         print('input muted')

         timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
         _memoria.set(audio_id, "last_played", timestamp)      
         # get random file from folder         
      
      wave_player = wave.open(filename, 'rb')
      frames = wave_player.readframes(chunk)

      ## update last played time 
      update_last_played_time(filename)

      # open stream to play audio 
      stream = p.open(
            format = FORMAT,
            channels = file_channels,
            rate = sample_rate,
            output = True)
      print('playing: ' + filename)    
             
      # read all file     
      while len(frames) > 0:            
            stream.write(frames)
            frames = wave_player.readframes(chunk)
      else:          
         stream.close()
         wave_player.close()         

         print('-----------------------')
         if GUI:
             display.set_state(MODO)

         if MODO == 'echo':
            print('input unmuted')
            asource.open()
         
         if MODO == 'oraculo':
            listen(0, 0)

   def playrandom(file_channels = 1):
      print('play random')
      # filename = random.choice(glob.glob(audio_folder + '*.wav'))
      file = get_file_from_list()
      filename = file['filename']
      print("open", filename)
      wave_player = wave.open(filename, 'rb')
      frames = wave_player.readframes(chunk)
      # open stream to play audio 
      
       ## update last played time
      update_last_played_time(filename)

      stream = p.open(
            format = FORMAT,
            channels = file_channels,
            rate = sample_rate,
            output = True)
      print('playing: ' + filename)
      # read all file     
      while len(frames) > 0:
            stream.write(frames)
            frames = wave_player.readframes(chunk)
      else:
         stream.close()
         wave_player.close()         

         if MODO == 'random':
            time.sleep(5)
            playrandom()

   def match_target_amplitude(sound, target_dBFS):
      change_in_dBFS = target_dBFS - sound.dBFS
      return sound.apply_gain(change_in_dBFS)

   def get_file_from_list(words = []):
      #_last_played_type = last_played_type
      with open(DATA_FILE_PATH) as f :
         data = json.load(f)
         print('len', len(data))         
         if len(words) == 0:                     
            min_ = min(data, key=lambda x: x["lastPlayed"]) 
            r = random.choice(data)
            #while min_["type"] == _last_played_type:
            #   min_ = min(data, key=lambda x: x["lastPlayed"])             
            #print("type", min_["type"], _last_played_type)                              
            #_last_played_type = min_["type"]
            #return min_
            return r
         else:            
            found_list = []
            hasFound = False                           
            for w in words:    
               for i in data:              
                  for t in i["tags"]:                     
                     if w == t:
                        print('found !', w, t)
                        print(i["filename"])
                        found_list.append(i)
                        hasFound = True                           
                        ## return i["filename"] 
            if hasFound:               
               r = random.choice(found_list)
            else :               
               r = random.choice(data)   
            return r



   def update_last_played_time(filename):
      print("update last played time")
      with open(DATA_FILE_PATH) as f :
         data = json.load(f)         
         for i in range(len(data)):
            if data[i]["filename"] == filename:
               data[i]["lastPlayed"] = time.time()
               update_data_file(data)  

   def update_data_file(data):
      with open(DATA_FILE_PATH,"w") as f:           
         json.dump(data, f, indent=4, sort_keys=True)
         print("data.json updated")


#   def input_text(list):
#      for prediction in list:
#         print(" " + prediction["text"] + " (" + str(prediction["confidence"]*100) + "%)")
#
#   def escutar(a, b):
#      r = sr.Recognizer()
#      with sr.Microphone() as source:                # use the default microphone as the audio source
#         audio = r.listen(source)                   # listen for the first phrase and extract it into audio data
#         print("You said " + r.recognize(audio))
#      try:
#         print("You said " + r.recognize(audio))    # recognize speech using Google Speech Recognition
#         thread(escutar, [0,0])
#      except LookupError:                            # speech is unintelligible
#         print("Could not understand audio")
#         thread(escutar, [0,0])
#
#  Oraculo, 
#  Comportamento para o próximo áudio 
   def timer(counter, last_played_time):            
      print('last_played_time', last_played_time)
      raise LookupError
      if time.time() - last_played_time > 5:
         print('time exceeded!')
         last_played_time = time.time()      
      else:
         timer(counter, last_played_time)

   def onNewAudio(filename, audio_id):
      if MODO == 'escuta':
         # start counter to go into playmode
         print('escuta')
      elif MODO == 'oraculo':
         next_audio = _memoria.getNext(audio_id)
         print(next_audio['text'])
         playfile(next_audio['filename'], next_audio['id'])
      elif MODO == 'echo':
         playfile(filename, audio_id) 
      elif MODO == 'random':
         playrandom()
      

   # Start
   init()

except KeyboardInterrupt:
   asource.close()
   sys.exit(0)

# except Exception as e:
   ## sys.stderr.write(str(e) + "\n")
   ## sys.exit(1)
                               
       
      

