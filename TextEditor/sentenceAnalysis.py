import json
import urllib
from PyDictionary import PyDictionary
import context

def getSuggestions(query, pos):
	print query
	dic = PyDictionary()
	query = reduce(lambda x,y: x+"+"+y, query.split())
	url = 'https://api.datamuse.com/words?ml=' + query
	response = json.loads(urllib.urlopen(url).read())
	response = response[:min(5, len(response))]
	response = map(lambda x: [x['word'], dic.meaning(x['word']).get(pos)] if dic.meaning(x['word']) != None else None), response)
	response = filter(lambda x: x[1] != None, response)
	return response

print getSuggestions('talk too much', 'Verb')