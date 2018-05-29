
from auditok import ADSFactory, AudioEnergyValidator, StreamTokenizer, player_for, from_file
import pyaudio
import wave
import sys
import random
import glob, os

try: 

   energy_threshold = 65
   duration = 5000 # seconds
   FORMAT = pyaudio.paInt16
   CHANNELS = 2
   # RATE = 44100
   CHUNK = 1024
   RECORD_SECONDS = 5000

   if len(sys.argv) > 1:
     energy_threshold = float(sys.argv[1])

   if len(sys.argv) > 2:
     duration = float(sys.argv[2])

   # record = True so that we'll be able to rewind the source.
   # max_time = 10: read 10 seconds from the microphone
   asource = ADSFactory.ads(record=True, max_time = duration)

   # params 
   sample_rate = asource.get_sampling_rate()
   sample_width = asource.get_sample_width()
   channels = asource.get_channels()
   chunk = 1024

   print(sample_width, sample_rate)
   
   validator = AudioEnergyValidator(sample_width=sample_width, energy_threshold = energy_threshold)
   tokenizer = StreamTokenizer(validator=validator, min_length=70, max_length=20000, max_continuous_silence=100)

   p = pyaudio.PyAudio()
   
   for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print((i,dev['name'],dev['maxInputChannels']))

   def savefile(data, start, end):
      print('-----------------------')
      print("Acoustic activity at: {0}--{1}".format(start, end))  
      filename = "teste_{0}_{1}.wav".format(start, end)
      waveFile = wave.open(filename, 'wb')
      waveFile.setnchannels(channels)
      waveFile.setsampwidth(sample_width)
      waveFile.setframerate(channels)
      waveFile.writeframes(b''.join(data))
      waveFile.close()
      playrandom()


   def playrandom():       
      asource.close()
      print('input muted')    
      # get random file from folder
      filename = random.choice(glob.glob("*.wav"))
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

   asource.open()

   print("\n  ** Make some noise (dur:{}, energy:{})...".format(duration, energy_threshold))

   tokenizer.tokenize(asource, callback=savefile)

   asource.close()

except KeyboardInterrupt:

   asource.close()
   sys.exit(0)

except Exception as e:
   
   sys.stderr.write(str(e) + "\n")
   sys.exit(1)
