from rest_framework.views import APIView, status, Request, Response
from rest_framework.pagination import PageNumberPagination
from .models import Pet
from .serializers import PetSerializer
from django.shortcuts import get_object_or_404
from groups.models import Group
from traits.models import Trait


class PetView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        if "trait" in request.query_params.keys():
            trait_param = request.query_params["trait"]
            trait = get_object_or_404(Trait, name=trait_param)
            pets = Pet.objects.filter(traits=trait)
        else:
            pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop("group")
        traits = serializer.validated_data.pop("traits", None)

        group_object = Group.objects.filter(
            scientific_name__iexact=group["scientific_name"]
        ).first()

        if group_object:
            pet_object = Pet.objects.create(
                **serializer.validated_data, group=group_object
            )
        else:
            new_group = Group.objects.create(**group)
            pet_object = Pet.objects.create(
                **serializer.validated_data, group=new_group
            )
        if traits:
            for trait in traits:
                trait_object = Trait.objects.filter(name__iexact=trait["name"]).first()

                if not trait_object:
                    trait_object = Trait.objects.create(**trait)
                pet_object.traits.add(trait_object)

        serializer = PetSerializer(pet_object)
        return Response(serializer.data, status.HTTP_201_CREATED)


class PetViewDetail(APIView):
    def get(self, request: Request, pet_id) -> Response:
        pet_object = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet_object)
        return Response(serializer.data, status.HTTP_200_OK)

    def patch(self, request: Request, pet_id) -> Response:
        pet_object = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop("group", None)
        traits = serializer.validated_data.pop("traits", None)

        if group:
            group_object = Group.objects.filter(
                scientific_name__iexact=group["scientific_name"]
            ).first()
            if group_object:
                pet_object.group = group_object

            else:
                new_group = Group.objects.create(**group)
                pet_object.group = new_group

            pet_object.group.save()

        if traits:
            for trait in traits:
                trait_object = Trait.objects.filter(name__iexact=trait["name"]).first()
                if trait_object:
                    for key, value in trait.items():
                        setattr(pet_object.traits, key, value)
                else:
                    trait_object = Trait.objects.create(**trait)
                pet_object.traits.add(trait_object)

        for key, value in serializer.validated_data.items():
            setattr(pet_object, key, value)

        pet_object.save()

        serializer = PetSerializer(pet_object)
        return Response(serializer.data)

    def delete(self, request: Request, pet_id) -> Response:
        pet_object = get_object_or_404(Pet, id=pet_id)
        pet_object.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
