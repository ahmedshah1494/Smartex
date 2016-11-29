import re
import json
import logging
from channels.sessions import channel_session
from models import *
import context, googleTest
import urllib
import threading
import hashlib
from django.core.files import File
from django.db import transaction

log = logging.getLogger(__name__)
MAX_CACHE_SIZE = 100
lock = threading.Lock()
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

@transaction.atomic
def evacuateCache():
    lock.acquire(True)
    cache = CachedItem.objects.all()
    cacheSize = len(cache)
    print cacheSize
    if cacheSize > MAX_CACHE_SIZE:
        toBeRemoved = cache[:cacheSize - MAX_CACHE_SIZE]
        for i in toBeRemoved:
            i.delete()
    lock.release()

@transaction.atomic
def cacheLookup(key, dataType, reply_channel):
    h = hashlib.sha224(key)
    item = CachedItem.objects.filter(key=h.hexdigest(), data_type=dataType)[0]
    res = json.loads(item.data_file.file.read())
    return res

@transaction.atomic
def cacheInsert(h, res, dataType, reply_channel):
    with open('TextEditor/cache/'+h.hexdigest(), 'w') as f:
        f.write(json.dumps(res))
    with open('TextEditor/cache/'+h.hexdigest(), 'r') as f:
        item = CachedItem(key=h.hexdigest(),
                            data_type= dataType,
                            data_file=File(f))
        item.save()
    evacuateCache()

def lookup(text, reply_channel):
    keywords = context.getKeywords(text)
    googleResponse = []
    replacements = []
    links = []
    response = {}
    evacuateCache()
    def lookUpGoogleKG():
        print 't1 started'
        for pn in keywords['PN']:
            # googleResponse.append(googleTest.lookup(pn))
            try:
                res = cacheLookup(pn, 'general info', reply_channel)
                response = {'general info': [res]}
                reply_channel.send({'text': json.dumps(response)})
                print 'cache hit on', pn
            except:
                res = googleTest.lookup(pn)
                h = hashlib.sha224(pn)
                cacheInsert(h, res, 'general info', reply_channel)
                response = {'general info': [res]}
                reply_channel.send({'text': json.dumps(response)})
                print 'cache miss on', pn
                

    def lookupLinks():
        print 't2 started'
        for pn in keywords['PN']:
            key = pn + reduce(lambda x,y: x + " " + y, keywords['VP'] + ['']) + " " + reduce(lambda x,y: x + " " + y,keywords["NP"] + [''])
            try:
                res = cacheLookup(key, 'links', reply_channel)
                print 'cache hit on', key
                response = {'links': [res]}
                reply_channel.send({'text': json.dumps(response)})
                print 'cache hit on', key
            except:
                res = googleTest.customSearch(key)
                h = hashlib.sha224(key)
                cacheInsert(h, res, 'links', reply_channel)
                response = {'links': [res]}
                reply_channel.send({'text': json.dumps(response)})
                print 'cache miss on', key
           
    # response['links'] = links
    # print googleResponse
    def lookupVP():
        print 't3 started'
        for vp in keywords['VP']:
            try:
                res = cacheLookup(vp, 'replacements', reply_channel)
                print 'cache hit on', vp
                response = {'replacements': res}
                reply_channel.send({'text': json.dumps(response)})
                print 'cache hit on', vp
            except:
                res = getSuggestions(vp, 'verb')
                h = hashlib.sha224(vp)
                cacheInsert(h, res, 'replacements', reply_channel)
                response = {'replacements': res}
                reply_channel.send({'text': json.dumps(response)})
                print 'cache miss on', vp
            # replacements += getSuggestions(vp, 'verb')
            # res = getSuggestions(vp, 'verb')
            # response = {'replacements': res}
            # reply_channel.send({'text': json.dumps(response)})
    def lookupNP():   
        print 't4 started'         
        for np in keywords['NP']:
            try:
                res = cacheLookup(np, 'replacements', reply_channel)
                print 'cache hit on', np
                response = {'replacements': res}
                reply_channel.send({'text': json.dumps(response)})
                print 'cache hit on', np
            except:
                res = getSuggestions(np, 'noun')
                h = hashlib.sha224(np)
                cacheInsert(h, res, 'replacements', reply_channel)
                response = {'replacements': res}
                reply_channel.send({'text': json.dumps(response)})
                print 'cache miss on', np
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
    
