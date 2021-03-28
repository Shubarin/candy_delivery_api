from api.models import Order
from api.serializers.assigns import AssignSerializer
from api.serializers.orders import OrderListSerializer, OrderSerializer
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class OrdersViewSet(viewsets.ViewSet):
    def create(self, request, *args, **kwargs):
        serializer = OrderListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        # Добавляем подробную информацию об ошибках валидации
        ids = [item.get('order_id') for item in request.data.get('data')]
        errors_list = serializer.errors['data']
        try:
            errors_id = [{'id': id, **e}
                         for id, e in zip(ids, errors_list) if e]
            message = {'validation_error': {'orders': errors_id}}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        except TypeError as e:
            return Response({'validation_error': 'bad request TypeError'},
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'validation_error': e.__class__.__name__},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def assign(self, request):
        serializer = AssignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def complete(self, request):
        try:
            complete_time = request.data.pop('complete_time')
            courier_id = request.data.pop('courier_id')
            order_id = request.data.get('order_id')
            order = Order.objects.filter(
                order_id=order_id,
                assign_courier__pk=courier_id,
                allow_to_assign=False).first()
            if not order:
                raise ValueError
        except Exception:
            return Response({"validation_error": 'bad request'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(data=request.data,
                                     context={'complete_time': complete_time,
                                              'courier_id': courier_id})
        serializer.is_valid()
        serializer.update(order, serializer.validated_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
