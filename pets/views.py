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

            serializer = PetSerializer(pets, many=True)
            return Response(serializer.data)

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
    def get(self, request, pet_id):
        pet_in_database = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet_in_database)
        return Response(serializer.data, status.HTTP_200_OK)

    def patch(self, request, pet_id):
        pet_in_database = get_object_or_404(Pet, id=pet_id)

        serializer = PetSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.pop("group", None)
        traits = serializer.validated_data.pop("traits", None)

        # if group:
        #     group_object = Group.objects.filter(
        #         scientific_name__iexact=group["scientific_name"]
        #     ).first()

        # if group_object:
        #     for key, value in group.items():
        #         setattr(pet_in_database.group, key, value)
        #     pet_in_database.group.save()
        # else:
        #     new_group = Group.objects.create(**group)
        #     pet_in_database.group = new_group
        #     pet_in_database.group.save()

        # if traits:
        #     pass

        for key, value in serializer.validated_data.items():
            setattr(pet_in_database, key, value)
        pet_in_database.save()
        serializer = PetSerializer(pet_in_database)

        return Response(serializer.data)

    def delete(self, request, pet_id):
        pet_in_database = get_object_or_404(Pet, id=pet_id)
        pet_in_database.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
