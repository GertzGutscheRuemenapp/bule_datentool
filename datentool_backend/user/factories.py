import factory
from factory.django import DjangoModelFactory, mute_signals
from django.contrib.gis.geos import Polygon
from faker import Faker

from .models import User, Profile, post_save, PlanningProcess, Scenario


faker = Faker('de-DE')


@mute_signals(post_save)
class ProfileFactory(DjangoModelFactory):
    class Meta:
        model = Profile

    admin_access = faker.pybool()
    can_create_process = faker.pybool()
    can_edit_basedata = faker.pybool()
    # We pass in profile=None to prevent UserFactory from creating another profile
    # (this disables the RelatedFactory)
    user = factory.SubFactory('datentool_backend.factories.UserFactory', profile=None)


@mute_signals(post_save)
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: faker.unique.name())

    # We pass in 'user' to link the generated Profile to our just-generated User
    # This will call ProfileFactory(user=our_new_user), thus skipping the SubFactory.
    profile = factory.RelatedFactory(ProfileFactory, factory_related_name='user')


class PlanningProcessFactory(DjangoModelFactory):
    class Meta:
        model = PlanningProcess

    name = faker.word()
    allow_shared_change = faker.pybool()


class ScenarioFactory(DjangoModelFactory):
    class Meta:
        model = Scenario

    name = faker.word()
    planning_process = factory.SubFactory(PlanningProcessFactory)
