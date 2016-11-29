import re
import json
import logging
from channels.sessions import channel_session
from models import *
import context, googleTest
import urllib
import threading

log = logging.getLogger(__name__)

def dictionaryLookup(word, pos):
    url = 'http://api.pearson.com/v2/dictionaries/ldoce5/entries?headword=%s&part_of_speech=%s&limit=2' % (word, pos)
    response = json.loads(urllib.urlopen(url).read())
    try:
        return map(lambda x: x['senses'][0]['definition'][0], response['results'])
    except:
        return []

def makeReverseDictionaryQuery(query):
    query = reduce(lambda x,y: x+"+"+y, query.split())
    url = 'https://api.datamuse.com/words?ml=' + query
    response = json.loads(urllib.urlopen(url).read())
    return response 

def getSuggestions(query, pos):
    print query
    response = makeReverseDictionaryQuery(query)
    # keyword = filter(lambda x: x[1] == 'NN' if pos == 'noun' else x[1] in ['VB','VBG','VBN','VBD','VBZ','NNS'], context.getPOSTag(query))
    response = filter(lambda x: 'tags' in x and pos[0] in x['tags'] and 'prop' not in x['tags'], response)
    response = response[:min(2, len(response))]
    response = map(lambda x: [query, x['word'], dictionaryLookup(x['word'],pos)], response)
    response = filter(lambda x: x[1] != None, response)
    return response

def lookup(text, reply_channel):
    keywords = context.getKeywords(text)
    googleResponse = []
    replacements = []
    links = []
    response = {}

    def lookUpGoogleKG():
        print 't1 started'
        for pn in keywords['PN']:
            # googleResponse.append(googleTest.lookup(pn))
            res = googleTest.lookup(pn)
            response = {'general info': [res]}
            reply_channel.send({'text': json.dumps(response)})

    def lookupLinks():
        print 't2 started'
        for pn in keywords['PN']:
            # links.append(googleTest.customSearch(pn + reduce(lambda x,y: x + " " + y, keywords['VP'] + ['']) + reduce(lambda x,y: x + " " + y,keywords["NP"] + [''])))
            res = (googleTest.customSearch(pn + reduce(lambda x,y: x + " " + y, keywords['VP'] + ['']) + reduce(lambda x,y: x + " " + y,keywords["NP"] + [''])))
            response = {'links': [res]}
            reply_channel.send({'text': json.dumps(response)})
    # response['links'] = links
    # print googleResponse
    def lookupVP():
        print 't3 started'
        for vp in keywords['VP']:
            # replacements += getSuggestions(vp, 'verb')
            res = getSuggestions(vp, 'verb')
            response = {'replacements': res}
            reply_channel.send({'text': json.dumps(response)})
    def lookupNP():   
        print 't4 started'         
        for np in keywords['NP']:
            # replacements += getSuggestions(np, 'noun')
            res = getSuggestions(np, 'noun')
            response = {'replacements': res}
            reply_channel.send({'text': json.dumps(response)})
    # response['replacements'] = replacements

    t1 = threading.Thread(target=lookUpGoogleKG)
    t2 = threading.Thread(target=lookupLinks)
    t3 = threading.Thread(target=lookupVP)
    t4 = threading.Thread(target=lookupNP)
    t1.start()
    t2.start()
    t3.start()
    t4.start()
    # return response

@channel_session
def ws_connect(message):
    # Extract the room from the message. This expects message.path to be of the
    # form /chat/{label}/, and finds a Room if the message path is applicable,
    # and if the Room exists. Otherwise, bails (meaning this is a some othersort
    # of websocket). So, this is effectively a version of _get_object_or_404.
    print message
    try:
        prefix, label = message['path'].decode('ascii').strip('/').split('/')
        if prefix != 'editor':
            log.debug('invalid ws path=%s', message['path'])
            return
        doc = Document.objects.get(id=label)
    except ValueError:
        log.debug('invalid ws path=%s', message['path'])
        return
    except Document.DoesNotExist:
        log.debug('ws room does not exist label=%s', label)
        return
    print message.channel_session
    message.channel_session['Document'] = doc.id

@channel_session
def ws_receive(message):
    docID = message.channel_session['Document']
    data = message['text']
    print data
    response = lookup(data, message.reply_channel)
    # message.reply_channel.send({'text': json.dumps(response)})

@channel_session
def ws_disconnect(message):
    return
    
