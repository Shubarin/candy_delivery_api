import datetime
from abc import ABC

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from api.models.couriers import Courier


class CourierSerializer(serializers.ModelSerializer):
    courier_id = serializers.IntegerField(validators=[UniqueValidator])

    class Meta:
        fields = ('courier_id', 'courier_type', 'regions', 'working_hours')
        model = Courier

    @classmethod
    def validate_courier_id(self, courier_id):
        courier = Courier.objects.filter(pk=courier_id).exists()
        if courier:
            raise ValidationError('invalid value courier_id'
                                  f'({courier_id}) this id already exists')
        return courier_id

    @staticmethod
    def validate_courier_type(courier_type):
        if courier_type not in ['foot', 'bike', 'car']:
            raise ValidationError('invalid value courier_type')
        return courier_type

    @staticmethod
    def validate_regions(regions):
        for num in regions:
            try:
                if int(num) < 1:
                    raise ValueError
            except ValueError:
                raise ValidationError('invalid values in regions list')
        return regions

    @staticmethod
    def validate_working_hours(working_hours):
        for period in working_hours:
            try:
                start, end = period.split('-')
                start = datetime.datetime.strptime(start, "%H:%M")
                end = datetime.datetime.strptime(end, "%H:%M")
            except ValueError:
                raise ValidationError('invalid values in working_hours list')
        return working_hours

    def to_internal_value(self, data):
        extra_field_in_request = any(
            [field not in self.fields for field in data])
        if extra_field_in_request:
            raise ValidationError(
                {"validation_error": 'extra fields in request'})
        if len(data) == 0:
            raise ValidationError('empty request')
        return super(CourierSerializer, self).to_internal_value(data)


class CourierListSerializer(serializers.Serializer):
    data = CourierSerializer(required=False, many=True, write_only=True)

    def create(self, validated_data):
        data = validated_data['data']
        if not data:
            raise ValidationError({'validation_error': 'empty request'})

        couriers = [Courier(**item) for item in data]
        return Courier.objects.bulk_create(couriers)

    # def update(self, instance, validated_data):
    #     print(instance)
    #     # Maps for id->instance and id->data item.
    #     courier_mapping = {courier.courier_id: courier for courier in instance}
    #     data_mapping = {item['courier_id']: item for item in validated_data}
    #
    #     # Perform creations and updates.
    #     ret = []
    #     for courier_id, data in data_mapping.items():
    #         courier = courier_mapping.get(courier_id, None)
    #         if courier is None:
    #             ret.append(self.child.create(data))
    #         else:
    #             ret.append(self.child.update(courier, data))
    #
    #     # Perform deletions.
    #     for courier_id, courier in courier_mapping.items():
    #         if courier_id not in data_mapping:
    #             courier.delete()
    #
    #     return ret
