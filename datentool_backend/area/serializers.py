from rest_framework import serializers

from .models import (SymbolForm, MapSymbol, LayerGroup, WMSLayer,
                     InternalWFSLayer, Source, AreaLevel, Area)


class SymbolFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymbolForm
        fields =  ('id', 'name', )


class MapSymbolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MapSymbol
        fields =  ('id', 'symbol', 'fill_color', 'stroke_color')


class LayerGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = LayerGroup
        fields = ('id', 'name', 'order')


class WMSLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = WMSLayer
        fields = ('id', 'name', 'group', 'layer_name', 'order', 'url')


class InternalWFSLayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalWFSLayer
        fields = ('id', 'symbol')


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('id', 'source_type', 'date', 'id_field', 'url', 'layer')


class AreaLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaLevel
        fields = ('id', 'name', 'order', 'source', 'layer')


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'area_level', 'geom', 'attributes')