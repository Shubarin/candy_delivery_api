from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response

from api.models import Order
from api.serializers.orders import OrderListSerializer


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderListSerializer(data=request.data)
        ids = [item.get('order_id') for item in request.data['data']]

        if serializer.is_valid():
            serializer.save()
            message = {'orders': [{'id': id} for id in ids]}
            return Response(message, status=status.HTTP_201_CREATED)

        errors_list = serializer.errors['data']
        errors_id = [{'id': id, 'detail': e}
                     for id, e in zip(ids, errors_list) if e]
        message = {'validation_error': {'orders': errors_id}}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
