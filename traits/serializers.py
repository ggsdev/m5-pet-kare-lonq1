from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Trait


class TraitSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    trait_name = serializers.CharField(
        max_length=20,
        source="name",
        validators=[UniqueValidator(queryset=Trait.objects.all())],
    )
    created_at = serializers.DateTimeField(read_only=True)
