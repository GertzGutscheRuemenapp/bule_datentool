from rest_framework import viewsets
from datentool_backend.utils.views import ProtectCascadeMixin
from datentool_backend.utils.permissions import (
    HasAdminAccessOrReadOnly, CanEditBasedata)

from .models import (DemandRateSet, DemandRate, ScenarioDemandRate)
from .serializers import (DemandRateSetSerializer,
                          DemandRateSerializer,
                          ScenarioDemandRateSerializer)


class DemandRateSetViewSet(ProtectCascadeMixin, viewsets.ModelViewSet):
    queryset = DemandRateSet.objects.all()
    serializer_class = DemandRateSetSerializer
    permission_classes = [HasAdminAccessOrReadOnly | CanEditBasedata]


class DemandRateViewSet(viewsets.ModelViewSet):
    queryset = DemandRate.objects.all()
    serializer_class = DemandRateSerializer
    permission_classes = [HasAdminAccessOrReadOnly | CanEditBasedata]


class ScenarioDemandRateViewSet(viewsets.ModelViewSet):
    queryset = ScenarioDemandRate.objects.all()
    serializer_class = ScenarioDemandRateSerializer
