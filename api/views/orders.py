from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.models import Order, Courier
from api.serializers.assigns import AssignSerializer
from api.serializers.orders import OrderListSerializer, OrderSerializer


class OrdersViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderListSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderListSerializer(data=request.data)
        ids = [item.get('order_id') for item in request.data.get('data')]

        if serializer.is_valid():
            serializer.save()
            message = {'orders': [{'id': id} for id in ids]}
            return Response(message, status=status.HTTP_201_CREATED)

        errors_list = serializer.errors['data']
        errors_id = [{'id': id, 'detail': e}
                     for id, e in zip(ids, errors_list) if e]
        message = {'validation_error': {'orders': errors_id}}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def assign(self, request):
        serializer = AssignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def complete(self, request):
        complete_time = request.data.pop('complete_time')
        courier_id = request.data.pop('courier_id')
        order = Order.objects.filter(order_id=request.data.get('order_id')).first()
        # TODO: оптимизировать проверку
        bad_request = False
        if not order:
            msg = 'invalid order_id'
            bad_request = True
        elif not order.assign_courier:
            msg = 'order not assign to courier'
            bad_request = True
        elif order.assign_courier.pk != courier_id:
            msg = 'order assign to another courier'
            bad_request = True
        elif order.allow_to_assign:
            msg = 'order is not assign'
            bad_request = True
        if bad_request:
            return Response({"validation_error": msg},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(data=request.data,
                                     context={'complete_time': complete_time,
                                              'courier_id': courier_id})
        serializer.is_valid()
        serializer.update(order, serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
