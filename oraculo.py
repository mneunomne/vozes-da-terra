
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
import uuid
import datetime 
import ftplib
import numpy as np
import memoria

SERVER_URL  = 'aurora.webfactional.com'
SERVER_PATH = 'webapps/vozes_da_terra/data'
USERNAME    = 'aurora'
PASSWORD    = 'matrizes33'

SAVE_FILES = False
UPLOAD_TO_SERVER = False
TRANSCRIPTION = True

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
   if (_os == 'Darwin') or (_os == 'Windows'): # macOs
      sample_rate = asource.get_sampling_rate()
   
   sample_width = asource.get_sample_width()
   channels = asource.get_channels()

   print(sample_width, sample_rate)
   
   validator = AudioEnergyValidator(sample_width=sample_width, energy_threshold = energy_threshold)
   tokenizer = StreamTokenizer(validator=validator, min_length=100, max_length=RECORD_SECONDS, max_continuous_silence=150) #  

   p = pyaudio.PyAudio()
   for i in range(p.get_device_count()):
      dev = p.get_device_info_by_index(i)
      print((i,dev['name'],dev['maxInputChannels']))
   _memoria = memoria.Memoria()

   def init():
      asource.open()
      print("\n  ** Make some noise (dur:{}, energy:{})...".format(duration, energy_threshold))
      tokenizer.tokenize(asource, callback=savefile)
      thread(escutar, [0,0])
      asource.close()       

   def escutar(a, b):
      r = sr.Recognizer()
      with sr.Microphone() as source:                # use the default microphone as the audio source
         audio = r.listen(source)                   # listen for the first phrase and extract it into audio data
      try:
         print("You said " + r.recognize(audio))    # recognize speech using Google Speech Recognition
         thread(escutar, [0,0])
      except LookupError:                            # speech is unintelligible
         print("Could not understand audio")
         thread(escutar, [0,0])

   def thread(func, params = [None, None]):
      try:
         _thread.start_new_thread( func, (params[0], params[1]) )
      except:
         print("error starting thread")

   def savefile(data, start, end):      
      # thread(test, [1, 2])
      print('-----------------------')
      print("Acoustic activity at: {0}--{1}".format(start, end))  
      filename = "audios/teste_{0}_{1}.wav".format(start, end)      
      # create folder if 'audios' doesnt exist
      if not os.path.exists(os.path.dirname(filename)):
          try:
              os.makedirs(os.path.dirname(filename))
          except OSError as exc: # Guard against race condition
              if exc.errno != errno.EEXIST:
                  raise
      waveFile = wave.open(filename, 'wb')
      waveFile.setnchannels(channels)
      waveFile.setsampwidth(sample_width)
      waveFile.setframerate(sample_rate)
      waveFile.writeframes(b''.join(data))
      waveFile.close()
      # salvar arquivo como data no data.json 
      audio_id = str(uuid.uuid4()) 
      saveToData(filename, start, end, audio_id)      
      # play next file
      playfile(filename)

   def saveToData(filename, start, end, audio_id):
      # calculate length in milsec 1s = 100
      length = end - start
      # get timestamp 
      timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
      
      # start process of analyzing audio ... (async)      
      thread(analyze_audio, [filename, audio_id])

      # upload file to server
      if UPLOAD_TO_SERVER:
         thread(upload, [filename, audio_id])
      
      audio_data = {
                     "id": audio_id,
                     "filename": filename,
                     "timestamp": timestamp,
                     "length": length,
                     "text": "",
                     "server_path": SERVER_URL + SERVER_PATH,
                     "tags": []           
                  }         
      
      _memoria.append(audio_data)

   def analyze_audio(filename, audio_id):      
      r = sr.Recognizer("pt-BR")
      print("reading file", filename)
      with sr.WavFile(filename) as source:              # use "test.wav" as the audio source
          audio = r.record(source)                        # extract audio data from the file
      try:
         print("Transcription: " + r.recognize(audio))   # recognize speech using Google Speech Recognition         
         text = r.recognize(audio)
         _memoria.set(audio_id, "text", text) 

      except LookupError:                                 # speech is unintelligible
          print("Could not understand audio")  

   def upload(filename, audio_data):
      session = ftplib.FTP(SERVER_URL, USERNAME, PASSWORD)
      # print('started ' + SERVER_URL + ' session' )      
      session.cwd(SERVER_PATH)
      file = open(filename,'rb')                       # file to send
      session.storbinary('STOR ' + filename, file)     # send the file
      print('file saved in server')
      # print(session.pwd(), ftplib.FTP.dir(session))
      file.close()                                     # close file and FTP
      session.quit()
      print('end session')

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
                               
      
      

