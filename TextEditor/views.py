from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse, Http404
# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models  import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.tokens import default_token_generator
from mimetypes import guess_type
# Imports the Comment class
from TextEditor.models import *
from TextEditor.forms import *
#EMAIL
from django.core.mail import send_mail
import datetime
import django.contrib.staticfiles
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.shortcuts import render_to_response
from django.db.models import Q
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core import serializers
import hashlib
import requests
import context
import json
import googleTest
import urllib
import boto3
citationDiv = '*=======================Citations=======================*'
@login_required
def loadEditor(request, docID):
	#print( int(docID) == 0)
	if int(docID) == 0:
		context = {}
	else:
		doc = Document.objects.get(id=docID)
		context = {'docID': docID,
					'title': doc.title}

	return render(request, 'editor.html', context)

@login_required
def saveDocument(request):
	if request.method != "POST":
		return render(request, 'editor.html', {})
	# #print request.POST['title']
	# path = default_storage.save('/path/to/file', ContentFile('new content'))
	try:
		title = request.POST['title']
	except:
		raise Http404("Wrong Request")
	#print title
	muser = MUser.objects.get(user_id=request.user.id)
	docs = Document.objects.filter(author_id=muser.id, title=title)
	if len(docs) > 0:
		doc = docs[0]
		# with open(doc.File.name,'w') as f:
		# 	mFile = File(f)
		# 	mFile.write(request.POST['content'])
		# 	mFile.write(citationDiv)
		# 	mFile.write(request.POST['citations'])

		# with open(doc.File.name,'r') as f:
		# 	mFile = File(f)
		# 	doc.File = mFile
		# 	doc.save()
		with open('TextEditor/Documents/'+muser.user.username+'.temp','w') as f:
			mFile = File(f)
			mFile.write(request.POST['content'])
			mFile.write(citationDiv)
			mFile.write(request.POST['citations'])
		s3 = boto3.client('s3')
		s3.upload_file('TextEditor/Documents/'+muser.user.username+'.temp', 'smartexdocuments', muser.user.username+title+'.txt')
		doc.date_modified=datetime.datetime.now()
		doc.save()
	else:
		# with open('TextEditor/Documents/%s.html' % title,'w') as f:
		# 	mFile = File(f)
		# 	mFile.write(request.POST['content'])
		# 	mFile.write(citationDiv)
		# 	mFile.write(request.POST['citations'])

		# with open('TextEditor/Documents/%s.html' % title,'r') as f:
		# 	mFile = File(f)
		# 	doc = Document(title=title, 
		# 		File=mFile, 
		# 		date_created=datetime.datetime.now(),
		# 		date_modified=datetime.datetime.now(),
		# 		author=MUser.objects.get(user_id=request.user.id))
		# 	doc.save()

		with open('TextEditor/Documents/'+muser.user.username+'.temp','w') as f:
			mFile = File(f)
			mFile.write(request.POST['content'])
			mFile.write(citationDiv)
			mFile.write(request.POST['citations'])
		s3 = boto3.client('s3')
		s3.upload_file('TextEditor/Documents/'+muser.user.username+'.temp', 'smartexdocuments', muser.user.username+title+'.txt')
		doc = Document(title=title, 
			File=mFile, 
			date_created=datetime.datetime.now(),
			date_modified=datetime.datetime.now(),
			author=MUser.objects.get(user_id=request.user.id))
		doc.save()

	return render(request, 'editor.html', {})

@login_required
def loadDashboard(request):
	print('________________LOAD DASHBOARD CALLED___________________________')
	context = {}
	muser = MUser.objects.get(user_id=request.user.id)
	documents = Document.objects.filter(author_id=muser.id)
	context['documents'] = documents
	context['first_name'] = request.user.first_name
	# #print documents[0].title
	# context['first_name'] = request.user.first_name
	return render(request, 'dashboard.html', context)

def loadDocument(request, docID):
	doc = Document.objects.get(id=docID)
	s3 = boto3.resource('s3')
	s3.meta.client.download_file('smartexdocuments', request.user.username+doc.title+'.txt', 'TextEditor/Documents/'+muser.user.username+'.temp')
	with open('TextEditor/Documents/'+muser.user.username+'.temp', 'r') as f:
		[content,citations] = doc.File.read().split(citationDiv)[:2]
	resp = {'content': content,
			'citations': citations}
	print (docID, content, citations)
	return HttpResponse(json.dumps(resp), content_type='application/json')	

@login_required
def getProfilePicture(request, uid):
	try:
		muser = MUser.objects.get(user_id=uid)
	except:
		raise Http404("User Does Not Exist")
	if not muser.profile.picture:
		content_type = guess_type(settings.MEDIA_ROOT+'John_Doe.jpg')
		print (os.getcwd())
		f = open(settings.MEDIA_ROOT+'profile_pictures/John_Doe.jpg')
		return HttpResponse(File(f), content_type=content_type)
	content_type = guess_type(muser.profile.picture.path)
	return HttpResponse(muser.profile.picture, content_type=content_type)

@login_required
def profile(request):
	muser = MUser.objects.get(user_id=request.user.id)
	print (muser.activation_key)

	user = muser.user
	context = {}
	# context['picture'] = '/grumblr/DP/'+uid

	context['full_name'] = user.first_name+' '+user.last_name
	context['username'] = user.username
	context['email'] = user.email
	return render(request, 'profile.html', context)	

@login_required
def updateProfile(request):
	muser = MUser.objects.get(user_id=request.user.id)
	form = UpdateUserInfoForm(request.POST)
	context={}
	context['form'] = form
	if request.method == 'GET':
		return render(request,'update_profile.html', context)
	if not (form.is_valid()):
		return render(request,'update_profile.html', context)
	for field in form.fields:
		if 'password' in field:
			continue
		if form.cleaned_data[field]:
			setattr(request.user, field, form.cleaned_data[field])
			request.user.save()
	if 'password1' in form.fields:
		print('updated password')
		request.user.set_password(form.cleaned_data['password1'])
		request.user.save()
	return redirect('/profile')
@transaction.atomic
def signup (request):
    print('______________WENT THOUGH SIGNUP______________')
    context = {}
    if request.method == 'GET':
        context['signupform'] = SignupNewUser()
        return render(request, 'signup.html',context)

    signupform = SignupNewUser(request.POST)
    context['signupform'] = signupform
    if not signupform.is_valid():
        return render(request, 'signup.html', context)

    new_user = User.objects.create_user(first_name = signupform.cleaned_data['first_name'],\
                                        last_name = signupform.cleaned_data['last_name'],\
                                        username = signupform.cleaned_data['username'], \
                                        email = signupform.cleaned_data['user_email'],\
                                        password=signupform.cleaned_data['password1'])
    #new_user = authenticate(username=request.POST['username'], \
    #                        password=request.POST['password1'])
    new_user.is_active = 0

    new_user.save()
    #new_user_profile = UserProfile( user = new_user,\
    #                                first_name = form.cleaned_data['first_name'],\
    #                                last_name = form.cleaned_data['last_name'])
    #new_user_profile.save()
    newUser = MUser(user=new_user)
    print(signupform.cleaned_data['username'])
    username = signupform.cleaned_data['username']
    h = hashlib.sha224(username.encode('utf-8'))
    token = h.hexdigest()[:40]
    newUser.activation_key = token
    newUser.save()
    email_body = """
            Welcome to grumblr, please click the link below to
            verify your email address and complete the registration
            of your account:
            http://smartexx.herokuapp.com/confirm/"""+token
            #% (request.get_host(),
                # reverse('confirm') +  "?username=" + new_user.username+"&token="+token
            #    reverse('confirm', args = (token))
            #)
    send_mail(subject= "Verify your email address",\
                message = email_body,\
                from_email= "grumblr@hotmail.com",
                recipient_list = [new_user.email])
    context['email'] = signupform.cleaned_data['user_email']

    return render(request, 'needs-confirmation.html', context)


@transaction.atomic()
def confirm_registration (request, token):
    context = {}
    errors = []
    #username = request.GET['username']
    #token = request.GET['token']
    try:
    	muser = MUser.objects.get(activation_key=token)
    except:
    	raise Http404("Activation Key Not Found")

    if  muser.user.is_active == False:
        muser.user.is_active = True
        muser.user.save()
        muser.save()
        # new_user = authenticate(username=muser.user.username, password=muser.user.password)
        # login(request, new_user)
        print('user confirmed')
        return redirect('/')
    else:
        errors.append('Your account has already been activated please login')
        context = { 'clicked_profile':muser.user.username, \
                    'statuses':[], \
                    'errors':errors}
        return redirect('/')

@login_required
def translate(request, text, lang):
	apiKey = "AIzaSyDJ0drwJEDA1FXVvCzq5TGjMNBLGQLC0HU"
	url = "https://www.googleapis.com/language/translate/v2?key="+apiKey+"&target="+lang+"&q="+text
	return HttpResponse(requests.get(url), content_type='application/json')

def dictionaryLookup(word, pos):
	url = 'http://api.pearson.com/v2/dictionaries/ldoce5/entries?headword=%s&part_of_speech=%s&limit=2' % (word, pos)
	response = json.loads(urllib.urlopen(url).read())
	try:
		return map(lambda x: x['senses'][0]['definition'][0], response['results'])
	except:
		return []

def getSuggestions(query, pos):
	print query
	query = reduce(lambda x,y: x+"+"+y, query.split())
	url = 'https://api.datamuse.com/words?ml=' + query
	response = json.loads(urllib.urlopen(url).read())
	response = response[:min(5, len(response))]
	response = map(lambda x: [query, x['word'], dictionaryLookup(x['word'],pos)], response)
	response = filter(lambda x: x[1] != None, response)
	return response

@login_required
def lookup(request, text):
	keywords = context.getKeywords(text)
	googleResponse = []
	replacements = []
	links = []
	response = {}
	for pn in keywords['PN']:
		googleResponse.append(googleTest.lookup(pn))
		links.append(googleTest.customSearch(pn + reduce(lambda x,y: x + " " + y, keywords['VP'] + ['']) + reduce(lambda x,y: x + " " + y,keywords["NP"] + [''])))
	response['general info'] = googleResponse
	response['links'] = links
	# print googleResponse
	for vp in keywords['VP']:
		replacements += getSuggestions(vp, 'verb')
	for np in keywords['NP']:
		replacements += getSuggestions(np, 'noun')
	response['replacements'] = replacements
	return HttpResponse(json.dumps(response), content_type='application/json')


