import json
from django.db import models
from django.contrib.gis.db import models as gis_models
from datentool_backend.base import NamedModel, JsonAttributes


class MapSymbol(models.Model):
    '''
    MapSymbols
    '''
    class Symbol(models.TextChoices):
        LINE = 'line'
        CIRCLE = 'circle'
        SQUARE = 'square'
        STAR = 'star'

    symbol = models.CharField(max_length=9, choices=Symbol.choices,
                              default=Symbol.CIRCLE)
    fill_color = models.CharField(max_length=9, default='#FFFFFF')
    stroke_color = models.CharField(max_length=9, default='#000000')


class LayerGroup(NamedModel, models.Model):
    """a Layer Group"""
    name = models.TextField()
    order = models.IntegerField(default=0)
    external = models.BooleanField(default=False)


class Layer(NamedModel, models.Model):
    """a generic layer"""
    name = models.TextField()
    group = models.ForeignKey(LayerGroup, on_delete=models.RESTRICT)
    layer_name = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        abstract = True


class WMSLayer(Layer):
    """a WMS Layer"""
    url = models.URLField()

    def __str__(self) -> str:
        return f'{self.__class__.__name__}: {self.url}'


class InternalWFSLayer(Layer):
    """an internal WFS Layer"""
    symbol = models.ForeignKey(MapSymbol, on_delete=models.CASCADE)


class SourceTypes(models.TextChoices):
    """SourceTypes"""
    WFS = 'WFS', 'WFS Source'
    FILE = 'FILE', 'File Source'


class Source(models.Model):
    """a generic source"""
    source_type = models.CharField(max_length=4, choices=SourceTypes.choices)
    date = models.DateField()
    id_field = models.TextField()
    url = models.URLField(null=True, blank=True)
    layer = models.TextField(null=True, blank=True)


class AreaLevel(NamedModel, models.Model):
    """an area level"""
    name = models.TextField()
    order = models.IntegerField(unique=True)
    source = models.ForeignKey(Source, on_delete=models.RESTRICT)
    layer = models.ForeignKey(InternalWFSLayer, on_delete=models.RESTRICT)


class Area(JsonAttributes, models.Model):
    """an area"""
    area_level = models.ForeignKey(AreaLevel, on_delete=models.RESTRICT)
    geom = gis_models.MultiPolygonField(geography=True)
    attributes = models.JSONField()

    def __str__(self) -> str:
        attributes = self.get_attributes()
        name = attributes.get('name',
                              attributes.get('gen', self.pk))
        return f'{self.__class__.__name__} ({self.area_level.name}): {name}'

