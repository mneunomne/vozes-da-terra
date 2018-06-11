import speech_recognition as sr
import nltk    
import pickle
from nltk import tokenize

tagger = pickle.load(open("nltk-port-tagger/tagger.pkl"))

def callback(recognizer, audio):                          # this is called from the background thread
    try:
        # received audio data, now need to recognize it
    	tokenizer(recognizer.recognize(audio))
    except LookupError:
        print("???")

def tokenizer(text):
	print('text', text)
	
	# tokens = tokenize.word_tokenize(text, language='portuguese')    
	# print('tokens', tokens)		
			
	portuguese_sent_tokenizer = nltk.data.load("tokenizers/punkt/portuguese.pickle")	
	sentences = portuguese_sent_tokenizer.tokenize(text)	
	tags = [tagger.tag(nltk.word_tokenize(sentence)) for sentence in sentences]

	# print('tokens', tokens)
	# tagged = nltk.pos_tag(tokens)
	# print('tagged', tagged)

r = sr.Recognizer()
r.listen_in_background(sr.Microphone(), callback)

import time
while True: time.sleep(0.01)