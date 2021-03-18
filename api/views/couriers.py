from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from api.models import Courier
from api.serializers.couriers import CourierListSerializer, CourierSerializer


class CouriersViewSet(viewsets.ModelViewSet):
    queryset = Courier.objects.all()
    serializer_class = CourierListSerializer

    def create(self, request, *args, **kwargs):
        serializer = CourierListSerializer(data=request.data)
        ids = [item.get('courier_id') for item in request.data['data']]

        if serializer.is_valid():
            serializer.save()
            message = {'couriers': [{'id': id} for id in ids]}
            return Response(message, status=status.HTTP_201_CREATED)

        errors_list = serializer.errors['data']
        errors_id = [{'id': id, 'detail': e}
                     for id, e in zip(ids, errors_list) if e]
        message = {'validation_error': {'couriers': errors_id}}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        courier = get_object_or_404(Courier, pk=self.kwargs.get('pk'))
        serializer = CourierSerializer(courier, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)