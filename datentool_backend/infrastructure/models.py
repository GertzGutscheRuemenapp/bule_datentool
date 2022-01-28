from django.db import models
from django.contrib.gis.db import models as gis_models

from datentool_backend.base import (NamedModel,
                                    JsonAttributes,
                                    DatentoolModelMixin,
                                    )
from datentool_backend.utils.protect_cascade import PROTECT_CASCADE

from datentool_backend.user.models import (PlanningProcess,
                                           Infrastructure,
                                           Service,
                                           )
from datentool_backend.population.models import Prognosis
from datentool_backend.modes.models import Mode, ModeVariant
from datentool_backend.demand.models import DemandRateSet


class Scenario(DatentoolModelMixin, NamedModel, models.Model):
    """BULE-Scenario"""
    name = models.TextField()
    planning_process = models.ForeignKey(PlanningProcess,
                                         on_delete=PROTECT_CASCADE)
    prognosis = models.ForeignKey(Prognosis, on_delete=PROTECT_CASCADE)
    modevariants = models.ManyToManyField(Mode,
                                          related_name='scenario_mode',
                                          blank=True,
                                          through='ScenarioMode')
    demandratesets = models.ManyToManyField(DemandRateSet,
                                            related_name='scenario_service',
                                            blank=True,
                                            through='ScenarioService')

class ScenarioMode(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=PROTECT_CASCADE)
    mode = models.ForeignKey(Mode, on_delete=PROTECT_CASCADE)
    variant = models.ForeignKey(ModeVariant, on_delete=PROTECT_CASCADE)


class ScenarioService(models.Model):
    scenario = models.ForeignKey(Scenario, on_delete=PROTECT_CASCADE)
    service = models.ForeignKey(Service, on_delete=PROTECT_CASCADE)
    demandrateset = models.ForeignKey(DemandRateSet, on_delete=PROTECT_CASCADE)


class Place(DatentoolModelMixin, JsonAttributes, NamedModel, models.Model):
    """location of an infrastructure"""
    name = models.TextField()
    infrastructure = models.ForeignKey(Infrastructure,
                                       on_delete=PROTECT_CASCADE)
    service_capacity = models.ManyToManyField(Service, related_name='place_services',
                                              blank=True, through='Capacity')
    geom = gis_models.PointField(srid=3857)
    attributes = models.JSONField()
    scenario = models.ForeignKey(Scenario, on_delete=PROTECT_CASCADE, null=True)

    def __str__(self) -> str:
        return (f'{self.__class__.__name__} ({self.infrastructure.name}): '
                f'{self.name}')


class Capacity(DatentoolModelMixin, models.Model):
    """Capacity of an infrastructure for a service"""
    place = models.ForeignKey(Place, on_delete=PROTECT_CASCADE)
    service = models.ForeignKey(Service, on_delete=PROTECT_CASCADE)
    capacity = models.FloatField(default=0)
    from_year = models.IntegerField(default=0)
    to_year = models.IntegerField(default=99999999)
    scenario = models.ForeignKey(Scenario, on_delete=PROTECT_CASCADE, null=True)


    class Meta:
        unique_together = ['place', 'service', 'from_year', 'scenario']

    def save(self, *args, **kwargs):
        """
        Update to_year in the last row and
        from_year in the current row before saving
        """
        last_row = Capacity.objects.filter(place=self.place,
                                     service=self.service,
                                     from_year__lt=self.from_year,
                                     scenario=self.scenario)\
            .order_by('from_year')\
            .last()
        if last_row:
            last_row.to_year = self.from_year - 1
            super(Capacity, last_row).save()

        next_row = Capacity.objects.filter(place=self.place,
                                           service=self.service,
                                           from_year__gt=self.from_year,
                                           scenario=self.scenario)\
            .order_by('from_year')\
            .first()
        if next_row:
            self.to_year = next_row.from_year - 1

        super().save(*args, **kwargs)




class FieldTypes(models.TextChoices):
    """enum for field types"""
    CLASSIFICATION = 'CLA', 'Classification'
    NUMBER = 'NUM', 'Number'
    STRING = 'STR', 'String'


class FieldType(DatentoolModelMixin, NamedModel, models.Model):
    """a generic field type"""
    field_type = models.CharField(max_length=3, choices=FieldTypes.choices)
    name = models.TextField()

    def validate_datatype(self, data) -> bool:
        """validate the datatype of the given data"""
        if self.field_type == FieldTypes.NUMBER:
            return isinstance(data, (int, float))
        if self.field_type == FieldTypes.STRING:
            return isinstance(data, (str, bytes))
        if self.field_type == FieldTypes.CLASSIFICATION:
            return data in self.fclass_set.values_list('value', flat=True)


class FClass(models.Model):
    """a class in a classification"""
    classification = models.ForeignKey(FieldType, on_delete=PROTECT_CASCADE)
    order = models.IntegerField()
    value = models.TextField()

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}: {self.classification.name}: '
                f'{self.order} - {self.value}')


class PlaceField(models.Model):
    """a field of a place"""
    attribute = models.TextField()
    unit = models.TextField()
    infrastructure = models.ForeignKey(Infrastructure, on_delete=PROTECT_CASCADE)
    field_type = models.ForeignKey(FieldType, on_delete=PROTECT_CASCADE)
    sensitive = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}: {self.attribute}'

