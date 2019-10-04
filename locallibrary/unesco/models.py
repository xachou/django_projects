from django.db import models
from django.urls import reverse

"""unesco_category, unesco_iso, unesco_region, unesco_site, and unesco_states)"""


class Category(models.Model):
    """ Representing a category of the cite: cultural/Natural/Mixed"""
    name = models.CharField(max_length=128)

    def __str__(self) :
        return self.name

class Site(models.Model):
    name = models.CharField(max_length=128)
    year = models.IntegerField(null=True)

    description = models.TextField(max_length=2000, null=True)
    justification = models.TextField(max_length=2000, null=True)
    area_hectares = models.FloatField(null=True, blank=True, default=None)
    longtitude = models.FloatField(null=True, blank=True, default=None)
    latitude = models.FloatField(null=True, blank=True, default=None)


    # One-To-Many relationship, because site can only belong to one category, but category can have multiple sites
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # One-To-Many relationship, because site can only belong to one region, but region can have multiple sites
    region = models.ForeignKey('Region', on_delete=models.SET_NULL, null=True)

    # One-To-Many relationship, because site can only belong to one iso (abbreviation of region), but iso can have multiple sites
    iso = models.ForeignKey('Iso', on_delete=models.SET_NULL, null=True)

    # One-To-Many relationship, because site can only belong to one states, but state can have multiple sites
    states = models.ForeignKey('States', on_delete=models.SET_NULL, null=True)


class Region(models.Model):
    name = models.CharField(max_length=200,default="")

    def __str__(self):
        return self.name


class Iso(models.Model):
    name = models.CharField(max_length=2,default="")

    def __str__(self):
        return self.name


class States(models.Model):
    name = models.CharField(max_length=100,default="")

    def __str__(self):
        return self.name

