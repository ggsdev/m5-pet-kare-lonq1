from rest_framework import serializers
from .models import Sexes
from groups.serializers import GroupSerializer
from traits.serializers import TraitSerializer


class PetSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50)
    age = serializers.IntegerField(min_value=1)
    weight = serializers.FloatField(min_value=1)
    sex = serializers.ChoiceField(choices=Sexes.choices, default=Sexes.DEFAULT)

    group = GroupSerializer()
    traits = TraitSerializer(many=True)
