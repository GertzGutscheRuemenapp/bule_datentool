import json

from django.db.models import ProtectedError
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from datentool_backend.utils.views import ProtectCascadeMixin
from datentool_backend.utils.permissions import (
    HasAdminAccessOrReadOnly, CanEditBasedata)

from .models import (Infrastructure,
                     FieldType,
                     Service,
                     Place,
                     Capacity,
                     PlaceField,
                     FClass,
                     )

from .serializers import (InfrastructureSerializer,
                          FieldTypeSerializer,
                          ServiceSerializer,
                          PlaceSerializer,
                          PlaceUpdateAttributeSerializer,
                          CapacitySerializer,
                          PlaceFieldSerializer,
                          FClassSerializer,
                          )


class CanPatchSymbol(permissions.BasePermission):
    """Permission Class for InfrastructureViewSet, patch of symbol, if user is
    authenticated and can edit basedata """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.profile.admin_access:
            return True
        if request.method in ['PATCH'] + list(permissions.SAFE_METHODS):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if (request.user.is_superuser or request.user.profile.admin_access
                or request.method in permissions.SAFE_METHODS):
            return True
        if (request.user.profile.can_edit_basedata and
                request.method in ('PATCH',) and (
                    len(request.data.keys()) == 0
                    or set(request.data.keys()) <= set(['symbol'])
                )
            ):
            return True
        return False


class InfrastructureViewSet(ProtectCascadeMixin, viewsets.ModelViewSet):
    queryset = Infrastructure.objects.all()
    serializer_class = InfrastructureSerializer
    permission_classes = [CanPatchSymbol]


class ServiceViewSet(ProtectCascadeMixin, viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [HasAdminAccessOrReadOnly | CanEditBasedata]


class PlaceViewSet(ProtectCascadeMixin, viewsets.ModelViewSet):

    serializer_class = PlaceSerializer
    serializer_action_class = {'update_attributes': PlaceUpdateAttributeSerializer}
    permission_classes = [HasAdminAccessOrReadOnly | CanEditBasedata]

    def get_serializer_class(self):
        return self.serializer_action_class.get(self.action,
                                                super().get_serializer_class())

    def get_queryset(self):
        queryset = Place.objects.all()
        service = self.request.query_params.get('service')
        if service:
            queryset = queryset.filter(service_capacity=service).distinct()
        return queryset

        #  user place_number in the query to get the default place...
        #scenario = self.request.query_params.get('scenario')
        #queryset_scenario = queryset\
            #.filter(scenario=scenario)
        #if not queryset_scenario:
            #queryset_scenario = queryset.filter(scenario=None)

        #return queryset_scenario

    @action(methods=['PATCH', 'PUT'], detail=True,
            permission_classes=[HasAdminAccessOrReadOnly | CanEditBasedata])
    def update_attributes(self, request, **kwargs):
        """
        route to update attributes of a place
        """
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(instance,
                                      data=request.data,
                                      partial=partial,
                                      context={'request': self.request, })
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class CapacityViewSet(ProtectCascadeMixin, viewsets.ModelViewSet):
    queryset = Capacity.objects.all()
    serializer_class = CapacitySerializer
    permission_classes = [HasAdminAccessOrReadOnly | CanEditBasedata]


class FieldTypeViewSet(ProtectCascadeMixin, viewsets.ModelViewSet):
    queryset = FieldType.objects.all()  # prefetch_related('classification_set',
                                         #         to_attr='classifications')
    serializer_class = FieldTypeSerializer
    permission_classes = [HasAdminAccessOrReadOnly | CanEditBasedata]


class FClassViewSet(ProtectCascadeMixin, viewsets.ModelViewSet):
    queryset = FClass.objects.all()
    serializer_class = FClassSerializer
    permission_classes = [HasAdminAccessOrReadOnly | CanEditBasedata]

    def perform_destroy(self, instance):
        """check, if there are referenced attributes"""
        place_fields = instance.classification.placefield_set.distinct()
        for place_field in place_fields:
            places = Place.objects.filter(infrastructure=place_field.infrastructure)
            for place in places:
                attr_dict = json.loads(place.attributes)
                if attr_dict.get(place_field.attribute) == instance.value:
                    if self.use_protection:
                        msg = f'Cannot delete {instance} because {place} has attributes {place.attributes} using it'
                        raise ProtectedError(msg, [place])
                    attr_dict.pop(place_field.attribute)
                    place.attributes = json.dumps(attr_dict)
                    place.save()
        instance.delete()


class PlaceFieldViewSet(ProtectCascadeMixin, viewsets.ModelViewSet):
    queryset = PlaceField.objects.all()
    serializer_class = PlaceFieldSerializer
    permission_classes = [HasAdminAccessOrReadOnly | CanEditBasedata]

    def perform_destroy(self, instance):
        """check, if there are referenced attributes"""
        places = Place.objects.filter(infrastructure=instance.infrastructure)
        for place in places:
            attr_dict = json.loads(place.attributes)
            if instance.attribute in attr_dict:
                if self.use_protection:
                    msg = f'Cannot delete "{instance}" because {place} has the attributes {place.attributes} using it'
                    raise ProtectedError(msg, [place])
                attr_dict.pop(instance.attribute)
                place.attributes = json.dumps(attr_dict)
                place.save()
        instance.delete()
