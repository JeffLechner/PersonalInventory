from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
	id = models.BigAutoField(primary_key=True)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	accountName = models.CharField(max_length=100)


class Profile(models.Model):
	profileId = models.UUIDField(primary_key=True)
	name = models.CharField(max_length=100)
	user = models.ForeignKey(User, on_delete=models.CASCADE)


class Place(models.Model):
	id = models.BigAutoField(primary_key=True)
	name = models.CharField(max_length=100)
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)


class Area(models.Model):
	id = models.BigAutoField(primary_key=True)
	name = models.CharField(max_length=100)
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	place = models.ForeignKey(Place, on_delete=models.CASCADE)


class Container(models.Model):
	id = models.BigAutoField(primary_key=True)
	name = models.CharField(max_length=100)
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	area = models.ForeignKey(Area, on_delete=models.CASCADE)


class InventoryItem(models.Model):
	profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
	itemId = models.UUIDField(primary_key=True)
	container = models.ForeignKey(Container, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	value = models.IntegerField()
	category = models.CharField(max_length=100)

	# interestPerTimeUnit = models.IntegerField()
	# timeUnit = models.DurationField()
	# compounded = models.BooleanField()
	# insuranceCoverage

	lentTo = models.CharField(max_length=100, blank=True, null=True)
	lentToFriend = models.BooleanField(default=False, blank=True, null=True)

	extraDetails = models.CharField(max_length=200, blank=True)

