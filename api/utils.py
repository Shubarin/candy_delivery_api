import datetime
from typing import List

from django.db.models import Avg, F, DateTimeField
from django.db.models.functions import Cast
from rest_framework.exceptions import ValidationError

from api.models import Order, Assign


class Interval:
    def __init__(self):
        self.working_hours = None
        self.delivery_hours = None

    @staticmethod
    def convert_str_to_time(intervals: List[str]):
        result = []
        for interval in intervals:
            try:
                start, end = interval.split('-')
                item = {'start': datetime.datetime.strptime(start, "%H:%M"),
                        'end': datetime.datetime.strptime(end, "%H:%M")}
                result.append(item)
            except ValueError:
                raise ValidationError('invalid values in intervals list')
        return result

    def set_working_hours(self, intervals: List[str]):
        self.working_hours = self.convert_str_to_time(intervals)

    def set_delivery_hours(self, intervals: List[str]):
        self.delivery_hours = self.convert_str_to_time(intervals)

    def delivery_allowed(self):
        if self.working_hours and self.delivery_hours:
            for delivery_hour in self.delivery_hours:
                for working_hour in self.working_hours:
                    if self.is_intervals_intersection(delivery_hour,
                                                      working_hour):
                        return True
        return False

    @staticmethod
    def is_intervals_intersection(a, b):
        return a['start'] <= b['end'] and a['end'] >= b['start']


def get_rating(courier):
    result_t = []
    for region in courier.regions:
        time_to_region = Order.objects.filter(
            region=region,
            assign_courier=courier,
        ).aggregate(
            average_difference=Avg((Cast('complete_time',
                                         output_field=DateTimeField())) -
                                   (Cast('assign_time',
                                         output_field=DateTimeField()))))
        average_difference = time_to_region['average_difference']
        if average_difference:
            result_t.append(average_difference.seconds)
    t = min(result_t) if result_t else 0
    return round((60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5, 2)


def get_earning(courier):
    coefficient = {
        'foot': 2,
        'bike': 5,
        'car': 9
    }
    n = Assign.objects.filter(courier_id=courier.courier_id,
                              orders__is_complete=True).count()
    total = n * 500 * coefficient[courier.courier_type]
    return total
