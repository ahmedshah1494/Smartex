from django import forms

from django.contrib.auth.models import User
from TextEditor.models import *

class UpdateUserInfoForm(forms.Form):
	first_name = forms.CharField(max_length=200, label='First Name', required=False)
	last_name = forms.CharField(max_length=200, label='Last Name', required=False)
	email = forms.EmailField(label='Email Address', required=False)
	password1 = forms.CharField(max_length=200, 
								widget = forms.PasswordInput(),
								label="Password", required=False)
	password2 = forms.CharField(max_length=200, 
								widget = forms.PasswordInput(),
								label="Confirm Password", required=False)
	def clean(self):
		# Calls our parent (forms.Form) .clean function, gets a dictionary
		# of cleaned data as a result
		cleaned_data = super(UpdateUserInfoForm, self).clean()
		# Confirms that the two password fields match

class SignupNewUser(forms.Form):
	first_name = forms.CharField(max_length=40, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'First Name'}))
	last_name = forms.CharField(max_length=40, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Last Name'}))
	username = forms.CharField(max_length = 20, widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Username'}))
	user_email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Email'}))
	password1 = forms.CharField(max_length = 200,label='Password',widget = forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Password'}))
	password2 = forms.CharField(max_length = 200,label='Confirm password', widget = forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'Confirm Password'}))
	def clean(self):
		cleaned_data = super(SignupNewUser, self).clean()
		password1 = cleaned_data.get('password1')
		password2 = cleaned_data.get('password2')
		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("Passwords did not match.")
		# Generally return the cleaned data we got from our parent.
		return cleaned_data

	def clean_username(self):

		username = self.cleaned_data.get('username')
		if User.objects.filter(username=username):
			raise forms.ValidationError("Username is already taken.")
		return username
	def clean_user_email(self):

		user_email = self.cleaned_data.get('user_email')
		if User.objects.filter(email=user_email):
			raise forms.ValidationError("Email is already taken.")
		return user_email
		
class shareForm(forms.Form):
	user_email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder': 'Email'}))
	def clean(self):
		cleaned_data = super(shareForm, self).clean()
		return cleaned_data