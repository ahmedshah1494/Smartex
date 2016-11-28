import nltk

def getKeywords(string):
	print string
	sentences = nltk.sent_tokenize(string)
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	sentences = [nltk.pos_tag(sent) for sent in sentences]
	result = {"NP": [], "PN": [], "VP": []}
	for sentence in sentences:
		print sentence
		grammars = [r"""
		  NP: {<DT|IN\$>?<JJ>*<NN>}   # chunk determiner/possessive, adjectives and noun
		  	  {<NNP><DT><NNP>}
		""",
		r"""
		  PN: {<NNP>+}               # chunk sequences of proper nouns
		""",
		r"""
		  VP: {<VB|VBG|VBN|VBD|NNS><DT|RB>*<JJ|RB>}               # chunk sequences of proper nouns
		""",]
		trees = []
		for grammar in grammars:
			cp = nltk.RegexpParser(grammar)
			trees.append(cp.parse(sentence))
		for t in trees:
			for i in t.subtrees(filter=(lambda x: x.label() in ["NP", 'PN', 'VP'])):
				result[i.label()].append(reduce(lambda x,y: x+' '+y, map(lambda a: a[0][0], i.pos())))
	return result

def getPOSTags(string):
	sentences = nltk.sent_tokenize(string)
	sentences = [nltk.word_tokenize(sent) for sent in sentences]
	sentences = [nltk.pos_tag(sent) for sent in sentences]
	return sentences[0]

# print getPOSTags('has a large house')
# print getKeywords("Obama talks too much.")

# def getMeaning(string):
# 	dic = PyDictionary()
# 	return dic.synonym(string)



# print getMeaning("bag")
