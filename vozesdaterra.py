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
import uuid
import datetime 
import ftplib
import numpy as np
import memoria
from pydub import AudioSegment
import nltk    
from nltk import tokenize
from argparse import ArgumentParser

from gui import *

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
parser.add_argument("-M", "--modo", dest="modo",
                    help="Modo de funcionamento", default="echo")

args = parser.parse_args()

sample_rate = int(args.sample_rate)
FORMAT = pyaudio.paInt16
CHANNELS = 2
CHUNK = 1024
chunk = CHUNK
GUI = False

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


# parametros de funcionamento
MODO = args.modo
DEBUG = args.DEBUG

SAVE_FILES = True
UPLOAD_TO_SERVER = False
TRANSCRIPTION = False

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

try:
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
      display = (root)

   if TRANSCRIPTION:
      # LOAD RECOGNIZER
      recognizer = sr.Recognizer("pt-BR")     
      # nltk vars
      stop_words = nltk.corpus.stopwords.words('portuguese')
      stemmer = nltk.stem.RSLPStemmer()           

   # print out sound devices
   if DEBUG:       
      print('sample rate',  sample_rate)      
      for i in range(p.get_device_count()):
         dev = p.get_device_info_by_index(i)
         print((i,dev['name'],dev['maxInputChannels']))   

   def init():
      if GUI:
         display.set_state('listening')
      
      if MODO == 'echo':
         asource.open()
         print("\n  ** Make some noise (dur:{}, energy:{})...".format(max_length, energy_threshold))      
         tokenizer.tokenize(asource, callback=savefile)      
         asource.close()
      elif MODO == 'random':
         playrandom()


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


   def stemm_text(text, audio_id):
      print('text', text)
      tokens = tokenize.word_tokenize(text, language='portuguese')    
      stemms = [stemmer.stem(i) for i in tokens if i not in stop_words]
      print('stemms', stemms)    
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

   def playfile(filename, audio_id = 0):    
      if GUI:
          display.set_state('playing')
      asource.close()      
      print('input muted')
      timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
      _memoria.set(audio_id, "last_played", timestamp)      
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
         if GUI:
             display.set_state('listening')

   def playrandom():
      filename = random.choice(glob.glob(audio_folder + '*.wav'))     
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
         playrandom()

   def match_target_amplitude(sound, target_dBFS):
      change_in_dBFS = target_dBFS - sound.dBFS
      return sound.apply_gain(change_in_dBFS)

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
#

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

except Exception as e:
   sys.stderr.write(str(e) + "\n")
   sys.exit(1)
                               
      
      

