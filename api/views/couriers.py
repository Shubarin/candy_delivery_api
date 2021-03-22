from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from api.models import Courier
from api.serializers.couriers import CourierListSerializer, CourierSerializer
from api.utils import get_rating, get_earning


class CouriersViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        serializer = CourierListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        ids = [item.get('courier_id') for item in request.data['data']]
        errors_list = serializer.errors['data']
        errors_ids = [{'id': id, 'detail': e}
                     for id, e in zip(ids, errors_list) if e]
        data = {'validation_error': {'couriers': errors_ids}}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        courier = get_object_or_404(Courier, pk=self.kwargs.get('pk'))
        serializer = CourierSerializer(courier, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        courier = get_object_or_404(Courier, pk=self.kwargs.get('pk'))
        serializer = CourierSerializer(courier)
        data = serializer.to_representation(courier)

        rating = get_rating(courier)
        if rating:
            data['rating'] = rating
        earning = get_earning(courier)
        if earning:
            data['earning'] = earning

        return Response(data, status=status.HTTP_200_OK)
