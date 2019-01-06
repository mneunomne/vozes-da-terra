import os, glob
import pyaudio
import random
import wave
import sys 
from argparse import ArgumentParser

parser = ArgumentParser()

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

p = pyaudio.PyAudio()

sample_rate = int(args.sample_rate)
FORMAT = pyaudio.paInt16
CHANNELS = 2
channels = CHANNELS
CHUNK = 1024
chunk = CHUNK
GUI = False

try:

   # LOAD PYAUDIO 
   p = pyaudio.PyAudio()

   def playrandom():
      filename = random.choice(glob.glob("audios/*.wav"))     
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
         print('-----------------------')

   playfile()

except KeyboardInterrupt:
   asource.close()
   sys.exit(0)

except Exception as e:
   sys.stderr.write(str(e) + "\n")
   sys.exit(1)