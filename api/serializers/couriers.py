import datetime
from collections import defaultdict

from api.models.couriers import Courier
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


class CourierSerializer(serializers.ModelSerializer):
    courier_id = serializers.IntegerField()

    class Meta:
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours')
        model = Courier

    def to_internal_value(self, data):
        extra_field_in_request = any(
            [field not in self.fields for field in data])
        if extra_field_in_request:
            raise ValidationError(
                {"validation_error": 'extra fields in request'})
        if len(data) == 0:
            raise ValidationError('empty request')
        return super(CourierSerializer, self).to_internal_value(data)

    def update(self, instance, validated_data):
        # Проверяем, что смена региона не помешает доставить заказ
        instance.check_change_regions(validated_data.get('regions'))
        # Проверяем, что смена рабочего времени не помешает доставить заказ
        instance.check_change_working_hours(
            validated_data.get('working_hours'))
        # Проверяем, что смена типа курьера не помешает доставить заказ
        instance.check_change_courier_type(validated_data.get('courier_type'))
        assign = instance.assign.filter(is_complete=False).first()
        if assign and assign.can_close():
            assign.is_complete = True
            assign.save()
        return super(CourierSerializer, self).update(instance, validated_data)

    @classmethod
    def validate_courier_id(self, courier_id):
        courier = Courier.objects.filter(pk=courier_id).first()
        if courier:
            raise ValidationError('invalid value courier_id: '
                                  f'({courier_id}) id already exists')
        return courier_id

    @staticmethod
    def validate_courier_type(courier_type):
        if courier_type not in ['foot', 'bike', 'car']:
            raise ValidationError('invalid value courier_type')
        return courier_type

    @staticmethod
    def validate_regions(regions):
        try:
            for num in regions:
                if int(num) < 1:
                    raise ValueError('invalid values in regions list')
            return regions
        except ValueError as e:
            raise ValidationError(e)

    @staticmethod
    def validate_working_hours(working_hours):
        try:
            for period in working_hours:
                # Проверяем что конец позже начала, т.к. рабочие часы
                # формируются максимум на одни сутки
                start, end = period.split('-')
                start = datetime.datetime.strptime(start, "%H:%M")
                end = datetime.datetime.strptime(end, "%H:%M")
                interval = end - start
                if interval.days >= 1 or interval.days < 0:
                    raise ValueError
            return working_hours
        except ValueError:
            raise ValidationError('invalid values in working_hours list')

class CourierListSerializer(serializers.Serializer):
    data = CourierSerializer(required=False, many=True, write_only=True)

    def create(self, validated_data):
        data = validated_data.get('data')
        if not data:
            raise ValidationError({'validation_error': 'empty request'})
        # проверяем что id в запросе уникальны
        couriers_ids = [item.get('courier_id') for item in data]
        if len(couriers_ids) != len(set(couriers_ids)):
            ids = defaultdict(int)
            for id in couriers_ids:
                ids[id] += 1
            failed_ids = [{'id': item} for item in ids if ids[item] != 1]
            raise ValidationError(
                {'validation_error': {'couriers': failed_ids}})
        couriers = [Courier(**item) for item in data]
        return Courier.objects.bulk_create(couriers)

    def to_representation(self, instance):
        data = {'couriers': [{'id': courier.pk} for courier in instance]}
        return data
