from django.db import models
from django.contrib.gis.db.models import MultiPolygonField
from datentool_backend.models import AreaLevel
from datentool_backend.utils.models import SingletonModel


class ProjectSetting(SingletonModel):
    project_area = MultiPolygonField(null=True, srid=3857)


class SiteSetting(SingletonModel):
    name = models.CharField(max_length=50, unique=True)
    title = models.TextField(default='Datentool')
    contact_mail = models.EmailField(default='', null=True, blank=True)
    logo = models.ImageField(null=True, blank=True)
    primary_color = models.CharField(default='#50AF32', max_length=30)
    secondary_color = models.CharField(default='#0390fc', max_length=30)
    welcome_text = models.TextField(default='Willkommen', null=True, blank=True)



