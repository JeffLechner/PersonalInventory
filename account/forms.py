from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Area, Container, InventoryItem, Place, Profile


class SignUpForm(UserCreationForm):
	email = forms.EmailField(
		label='',
		max_length=254,
		widget=forms.EmailInput(
			attrs={
				"placeholder": "Email",
				"class": "form-control"
			}
		)
	)

	username = forms.CharField(
		label='',
		max_length=30,
		min_length=5,
		required=True,
		widget=forms.TextInput(
			attrs={
				"placeholder": "Username",
				"class": "form-control"
			}
		)
	)

	password1 = forms.CharField(
		label='',
		max_length=30,
		min_length=8,
		required=True,
		widget=forms.PasswordInput(
			attrs={
				"placeholder": "Password",
				"class": "form-control"
			}
		)
	)

	password2 = forms.CharField(
		label='',
		max_length=30,
		min_length=8,
		required=True,
		widget=forms.PasswordInput(
			attrs={
				"placeholder": "Confirm Password",
				"class": "form-control"
			}
		)
	)

	class Meta:
		model = User
		fields = ('username', 'email', 'password1', 'password2')


class InventoryItemForm(forms.ModelForm):
	class Meta:
		model = InventoryItem
		fields = ('name', 'value', 'category', 'extraDetails')

	name = forms.CharField(max_length=100)
	value = forms.IntegerField(min_value=0)
	category = forms.CharField(max_length=100)
	extraDetails = forms.CharField(max_length=200)


class ContainerForm(forms.ModelForm):
	class Meta:
		model = Container
		fields = ('name',)

	name = forms.CharField(max_length=100)


class PlaceForm(forms.ModelForm):
	class Meta:
		model = Place
		fields = ('name',)

	name = forms.CharField(max_length=100)


class AreaForm(forms.ModelForm):
	class Meta:
		model = Area
		fields = ('name',)

	name = forms.CharField(max_length=100)


class SelectProfileForm(forms.Form):
	id = forms.UUIDField()


class SearchItemsForm(forms.Form):
	query = forms.CharField(max_length=100)


class LendForm(forms.Form):
	toFriend = forms.BooleanField(required=False)
	name = forms.CharField(max_length=100)


class ProfileForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ('name',)
	name = forms.CharField(max_length=100)
