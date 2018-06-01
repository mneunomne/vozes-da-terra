import speech_recognition as sr
import _thread
import sys 

filename = 'teste_1522_1763.wav'

if len(sys.argv) > 1:
     filename = sys.argv[1]
     print('input filename:', filename)

def getTextFromAudio():  
    print('escutando...')
    r = sr.Recognizer("pt-BR")
    with sr.WavFile(filename) as source:                # use the default microphone as the audio source
        audio = r.listen(source)                   # listen for the first phrase and extract it into audio data
    try:
        print("You said " + r.recognize(audio))    # recognize speech using Google Speech Recognition
    except LookupError:                            # speech is unintelligible
        print("Could not understand audio")    


def run():
    try:
        _thread.start_new_thread( speak_async,() )
        print('ola')    
    except:
        print ("Error: unable to start thread")

run()

while 1:
   pass