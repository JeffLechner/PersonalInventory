import uuid
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import CharField
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.exceptions import NoReverseMatch

from .forms import (AreaForm, ContainerForm, InventoryItemForm, LendForm,
                    PlaceForm, ProfileForm, SearchItemsForm, SelectProfileForm,
                    SignUpForm)
from .models import Account, Area, Container, InventoryItem, Place, Profile

CharField.register_lookup(Lower)


def group(flat):
	if len(flat) == 0:
		return flat
	grouped = [flat[i:i + 3] for i in range(0, len(flat), 3)]
	if len(grouped[-1]) != 3:
		for i in range(3 - len(grouped[-1])):
			grouped[-1].append(None)

	return grouped


def doUrlRedirect(request):
	redirect_url = request.GET.get('r', default='users:dashboard')
	try:
		return redirect(redirect_url)
	except NoReverseMatch:
		return redirect('users:dashboard')


def getProfile(request):
	selectedProfile = request.session.get('selectedProfile', default=None)
	try:
		return Profile.objects.get(pk=selectedProfile)
	except Profile.DoesNotExist:
		profiles = Profile.objects.filter(user=request.user)
		if len(profiles) == 1:
			profile = profiles[0]
			request.session['selectedProfile'] = str(profile.profileId)
			return profile
		else:
			raise


def requireSelectedProfile(func):
	@wraps(func)
	def inner(request, *args, **kwargs):
		try:
			return func(request, *args, **kwargs, profile=getProfile(request))
		except Profile.DoesNotExist:
			return redirect('/selectProfile', r=request.path)

	return inner


@login_required
def addProfile(request):
	form = ProfileForm()
	if request.method == 'POST':
		form = ProfileForm(request.POST)
		if form.is_valid():
			profile = form.save(commit=False)
			profile.profileId = uuid.uuid4()
			profile.user = request.user
			profile.save()
			return doUrlRedirect(request)

	return render(request, 'app/addProfile.html', {
		'form': form
	})


@login_required
def selectProfile(request):
	print(dict(request.session))
	profiles = Profile.objects.filter(user=request.user)
	if request.method == 'GET':
		selectedProfile = request.session.get('selectedProfile')
		force = request.GET.get('f')

		if not force == 't' and ((selectedProfile is not None and len(profiles.filter(pk=selectedProfile)) == 1) or len(profiles) == 1):
			request.session['selectedProfile'] = str(profiles[0].profileId)
			return doUrlRedirect(request)
	elif request.method == 'POST':
		form = SelectProfileForm(request.POST)
		if form.is_valid():
			print(str(form.cleaned_data['id']))
			request.session['selectedProfile'] = str(form.cleaned_data['id'])
			return doUrlRedirect(request)

	return render(request, 'app/selectProfile.html', {
		'profiles': group(profiles),
		'form': SelectProfileForm()
	})


def signup_view(request):
	if request.user.is_authenticated:
		return redirect('users:dashboard')
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password1')
			user = authenticate(username=username, password=password)
			login(request, user)
			Account(accountName=username, user=user).save()
			profile = Profile(name=username, user=user, profileId=uuid.uuid4())
			profile.save()
			request.session['selectedProfile'] = str(profile.profileId)
			return redirect('users:dashboard')
		else:
			messages.error(request, 'Correct the errors below')
	else:
		form = SignUpForm()

	return render(request, 'app/signup.html', {'form': form})


def home_view(request):
	return render(request, 'app/home.html')


@login_required
@requireSelectedProfile
def dashboard_view(request, profile):
	places = Place.objects.filter(profile=profile)
	items = InventoryItem.objects.filter(profile=profile)
	totalValue = 0
	for item in items:
		totalValue += item.value
	areas = Area.objects.filter(profile=profile)

	return render(request, 'app/dashboard.html', {
		'profile': profile,
		'items': items,
		'totalValue': totalValue,
		'form': InventoryItemForm(),
		'searchItemsForm': SearchItemsForm(),
		'orderedPlaces': group(places),
		'areas': areas
	})


@login_required
@requireSelectedProfile
def viewPlace(request, profile, pk):
	place = get_object_or_404(Place, pk=pk)
	if place.profile != profile:
		return redirect('/dashboard')
	areas = Area.objects.filter(place=place)

	return render(request, 'app/viewPlace.html', {
		'orderedAreas': group(areas),
		'place': place,
		'profile': profile
	})


@login_required
@requireSelectedProfile
def addPlace(request, profile):
	if request.method == 'POST':
		form = PlaceForm(request.POST)
		if form.is_valid():
			place = form.save(commit=False)
			place.profile = profile
			place.save()
			return doUrlRedirect(request)

	return render(request, 'app/addPlace.html', {
		'form': PlaceForm(),
		'r': request.GET.get('r', default='/dashboard')
	})


@login_required
@requireSelectedProfile
def deletePlace(request, profile, pk):
	place = Place.objects.get(pk=pk)
	if place.profile != profile:
		return doUrlRedirect(request)

	if request.method == 'POST':
		place.delete()
	elif request.method == 'GET':
		return render(request, 'app/deletePlace.html', {
			'profile': profile,
			'place': place,
			'r': request.GET.get('r', default='/dashboard'),
		})

	return doUrlRedirect(request)


@login_required
@requireSelectedProfile
def viewArea(request, profile, pk):
	area = get_object_or_404(Area, pk=pk)

	if area.profile != profile:
		return redirect('/dashboard')

	containers = Container.objects.filter(area=area)

	return render(request, 'app/viewArea.html', {
		'orderedContainers': group(containers),
		'area': area,
		'profile': profile,
	})


@login_required
@requireSelectedProfile
def addArea(request, profile, pk):
	place = get_object_or_404(Place, pk=pk)
	if request.method == 'POST':
		form = AreaForm(request.POST)
		if form.is_valid():
			area = form.save(commit=False)
			area.place = place
			area.profile = profile
			area.save()
			return doUrlRedirect(request)

	return render(request, 'app/addArea.html', {
		'form': AreaForm(),
		'r': request.GET.get('r', default='/dashboard')
	})


@login_required
@requireSelectedProfile
def deleteArea(request, profile, pk):
	area = Area.objects.get(pk=pk)
	if area.profile != profile:
		return doUrlRedirect(request)

	if request.method == 'POST':
		area.delete()
	elif request.method == 'GET':
		return render(request, 'app/deleteArea.html', {
			'profile': profile,
			'area': area,
			'r': request.GET.get('r', default='/dashboard'),
		})

	return doUrlRedirect(request)


@login_required
@requireSelectedProfile
def viewContainer(request, profile, pk):
	container = get_object_or_404(Container, pk=pk)
	if container.profile != profile:
		return redirect('/dashboard')

	items = InventoryItem.objects.filter(profile=profile)

	return render(request, 'app/viewContainer.html', {
		'profile': profile,
		'items': items,
		'container': container,
		'form': InventoryItemForm(),
	})


@login_required
@requireSelectedProfile
def addContainer(request, profile, pk):
	area = get_object_or_404(Area, pk=pk)
	if request.method == 'POST':
		form = ContainerForm(request.POST)
		if form.is_valid():
			container = form.save(commit=False)
			container.area = area
			container.profile = profile
			container.save()
			return doUrlRedirect(request)

	return render(request, 'app/addContainer.html', {
		'form': ContainerForm(),
		'r': request.GET.get('r', default='/dashboard')
	})


@login_required
@requireSelectedProfile
def deleteContainer(request, profile, pk):
	container = Container.objects.get(pk=pk)
	if container.profile != profile:
		return doUrlRedirect(request)

	if request.method == 'POST':
		container.delete()
	elif request.method == 'GET':
		return render(request, 'app/deleteContainer.html', {
			'profile': profile,
			'container': container,
			'r': request.GET.get('r', default='/dashboard'),
		})

	return doUrlRedirect(request)


@login_required
@requireSelectedProfile
def addItem(request, profile, pk):
	form = InventoryItemForm()
	container = get_object_or_404(Container, pk=pk)
	if request.method == 'POST':
		form = InventoryItemForm(request.POST)
		if form.is_valid():
			item = form.save(commit=False)
			item.container = container
			item.profile = profile
			item.itemId = uuid.uuid4()
			item.save()
			return doUrlRedirect(request)

	return render(request, 'app/addItem.html', {
		'form': form,
		'r': request.GET.get('r', default='/dashboard')
	})


@login_required
@requireSelectedProfile
def editItem(request, profile, pk):
	old = InventoryItem.objects.get(pk=pk)
	if old.profile != profile:
		return doUrlRedirect(request)
	if request.method == 'POST':
		form = InventoryItemForm(request.POST)
		if form.is_valid():
			item = form.save(commit=False)
			item.itemId = pk
			item.profile = profile
			item.container = old.container
			item.save()

	return doUrlRedirect(request)


@login_required
@requireSelectedProfile
def deleteItem(request, profile, pk):
	item = InventoryItem.objects.get(pk=pk)
	if item.profile != profile:
		return doUrlRedirect(request)

	if request.method == 'POST':
		item.delete()
	elif request.method == 'GET':
		return render(request, 'app/deleteItem.html', {
			'profile': profile,
			'item': item,
			'r': request.GET.get('r', default='/dashboard'),
		})

	return doUrlRedirect(request)


@login_required
@requireSelectedProfile
def lendItem(request, profile, pk):
	item = get_object_or_404(InventoryItem, pk=pk)
	if item.profile != profile:
		return doUrlRedirect(request)

	form = LendForm(request.POST)
	if request.method == 'POST':
		if form.is_valid():
			item.lentToFriend = form.cleaned_data['toFriend']
			item.lentTo = form.cleaned_data['name']
			item.save()
			return doUrlRedirect(request)

	return render(request, 'app/lendItem.html', {
		'item': item,
		'profile': profile,
		'form': form,
	})


@login_required
@requireSelectedProfile
def returnItem(request, profile, pk):
	item = get_object_or_404(InventoryItem, pk=pk)
	if item.profile != profile:
		return doUrlRedirect(request)

	item.lentToFriend = None
	item.lentTo = None
	item.save()
	return doUrlRedirect(request)


@login_required
@requireSelectedProfile
def searchItems(request, profile):
	if request.method == 'POST':
		form = SearchItemsForm(request.POST)
		if form.is_valid():
			query = form.cleaned_data['query']

			items = InventoryItem.objects.filter(profile=profile, name__lower__contains=query)

			return render(request, 'app/searchItems.html', {
				'profile': profile,
				'items': items,
				'query': query,
				'searchItemsForm': form
			})

	return redirect('users:dashboard')
