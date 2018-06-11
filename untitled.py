import nltk    
from nltk import tokenize


sents = ["aqui jaz um jarro", "aqui é o que é", "alo alo alo"]






stop_words = nltk.corpus.stopwords.words('portuguese')
stemmer = nltk.stem.RSLPStemmer()

def stemm_text(text):
	print('text', text)
	tokens = tokenize.word_tokenize(text, language='portuguese')    
	tokens = [stemmer.stem(i) for i in tokens if i not in stop_words]
	print('tokens', tokens)		
	return tokens

stemm_text("aqui na aldeia pankararu nós procuramos uma nova forma de lidar com a ancestralidade e a questão indígena e etc e tal")