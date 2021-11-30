from rest_framework import viewsets
# import for vector-tile functionality
#from django.views.generic import DetailView
#from vectortiles.mixins import BaseVectorTileView
#from django.views.generic import ListView
#from vectortiles.postgis.views import MVTView

from .models import (Raster, PopulationRaster, Gender, AgeClassification,
                     AgeGroup, DisaggPopRaster, Prognosis, PrognosisEntry,
                     Population, PopulationEntry, PopStatistic, PopStatEntry,
                     RasterCell)
from .serializers import (RasterSerializer, PopulationRasterSerializer,
                          GenderSerializer, AgeClassificationSerializer,
                          AgeGroupSerializer, DisaggPopRasterSerializer,
                          PrognosisSerializer, PrognosisEntrySerializer,
                          PopulationSerializer, PopulationEntrySerializer,
                          PopStatisticSerializer, PopStatEntrySerializer)


class RasterViewSet(viewsets.ModelViewSet):
    queryset = Raster.objects.all()
    serializer_class = RasterSerializer


class PopulationRasterViewSet(viewsets.ModelViewSet):
    queryset = PopulationRaster.objects.all()
    serializer_class = PopulationRasterSerializer






#class RasterCellTileViewSet(MVTView, DetailView):
    #"""Due to Cellcode geometry, implementation of vector tiles"""
    #model = Raster
    #vector_tile_fields = ('name', )

    #def get_vector_tile_layer_name(self):
        #return self.get_object().name

    #def get_vector_tile_queryset(self):
        #return self.get_object().rastercell.all()

    #def get(self, request, *args, **kwargs):
        #self.object = self.get_object()
        #return BaseVectorTileView.get(self,request=request, z=kwargs.get('z'), x=kwargs.get('x'), y=kwargs.get('y'))


class GenderViewSet(viewsets.ModelViewSet):
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer


class AgeClassificationViewSet(viewsets.ModelViewSet):
    queryset = AgeClassification.objects.all()
    serializer_class = AgeClassificationSerializer


class AgeGroupViewSet(viewsets.ModelViewSet):
    queryset = AgeGroup.objects.all()
    serializer_class = AgeGroupSerializer


class DisaggPopRasterViewSet(viewsets.ModelViewSet):
    queryset = DisaggPopRaster.objects.all()
    serializer_class = DisaggPopRasterSerializer


class PrognosisViewSet(viewsets.ModelViewSet):
    queryset = Prognosis.objects.all()
    serializer_class = PrognosisSerializer


class PrognosisEntryViewSet(viewsets.ModelViewSet):
    queryset = PrognosisEntry.objects.all()
    serializer_class = PrognosisEntrySerializer


class PopulationViewSet(viewsets.ModelViewSet):
    queryset = Population.objects.all()
    serializer_class = PopulationSerializer


class PopulationEntryViewSet(viewsets.ModelViewSet):
    queryset = PopulationEntry.objects.all()
    serializer_class = PopulationEntrySerializer


class PopStatisticViewSet(viewsets.ModelViewSet):
    queryset = PopStatistic.objects.all()
    serializer_class = PopStatisticSerializer


class PopStatEntryViewSet(viewsets.ModelViewSet):
    queryset = PopStatEntry.objects.all()
    serializer_class = PopStatEntrySerializer
