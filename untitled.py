import nltk    
from nltk import tokenize

sents = [	"aqui jaz um jarro", 
			"aqui é o que é", "alo alo alo",
			"aba nada chove conduzir",
			"pai nosso que estás no céu",
			"eu amo você",
			"fulana sente medo da chuv",
			"que deus traga muitas coisas boas para nós",
			"pela memória do povo pankararu",
			"a voz da terra",
			"alo alo alo",
			"a",
			"oi",
			"como funciona",
			"olá dona vilma",
			"salve nossa senhora",
			"queria colocar pro mundo inteiro escutar",
			"ola ola ola",
			"quero mandar uma mensagem de muito carinho para todos os que estão escutando a minha voz aqui quem fala é dona bárbara joaquina de jesus, falando da aldeia brejo dos padros em pernambuco",
			"mandar uma mensagem para o encatado e pedir a palavra",
			"mandar uma lembrança pra minha vózinha amada",
			"ola tudo bom",
			"quem está falando",
			"como funciona",
			"alo alo alo",
			"a musica diz muito sobre todos nós",
			"queria fazer um pedido pro senhor prefeito do município de tacaratu"]

stop_words = nltk.corpus.stopwords.words('portuguese')
stemmer = nltk.stem.RSLPStemmer()

def stemm_text(text):
	print('text', text)
	tokens = tokenize.word_tokenize(text, language='portuguese')    
	tokens = [stemmer.stem(i) for i in tokens if i not in stop_words]
	print('tokens', tokens)		
	return tokens

stemm_text("aqui na aldeia pankararu nós procuramos uma nova forma de lidar com a ancestralidade e a questão indígena e etc e tal")