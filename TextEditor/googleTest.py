"""Example of Python client calling Knowledge Graph Search API."""
import json
import urllib

def lookup(query):
	api_key = 'AIzaSyBDe57yDVtBC9o3o3DT6i2Ld2zBc5nSlno'
	service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
	params = {
	    'query': query,
	    'limit': 1,
	    'indent': True,
	    'key': api_key,
	}
	url = service_url + '?' + urllib.urlencode(params)
	response = json.loads(urllib.urlopen(url).read())
	if 'itemListElement' in response:
		return response['itemListElement']
	else:
		return {}
	for element in response['itemListElement']:
		print element
		print("________________________________\n\n\n\n")
		print element['result']['name'] + ' (' + str(element['resultScore']) + ')' + element['result']['description']

def customSearch(query):
	api_key = 'AIzaSyBDe57yDVtBC9o3o3DT6i2Ld2zBc5nSlno'
	service_url = 'https://www.googleapis.com/customsearch/v1'
	params = {
	    'q': query,
	    'cx': '011154718897604334069:te05mruh56s',
	    'key': api_key,
	}
	url = service_url + '?' + urllib.urlencode(params)
	response = json.loads(urllib.urlopen(url).read())
	# print query, response['items']
	if 'items' in response:
		return response['items']
	else:
		return []

	
# print cusomSearch('john lennon')