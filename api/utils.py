import datetime
from collections import defaultdict
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
    result_times = {int(region): [] for region in courier.regions}
    orders = Order.objects.filter(
        assign_courier=courier,
        is_complete=True).order_by('complete_time')
    prev_complete = None
    for order in orders:
        if prev_complete is None:
            time_delivery = order.complete_time - order.assign_time
        else:
            time_delivery = order.complete_time - prev_complete
        prev_complete = order.complete_time
        result_times[order.region].append(time_delivery.seconds)
    result_t = []
    for region, values in result_times.items():
        if values:
            average_difference = sum(values) / len(values)
            result_t.append(average_difference)
    t = min(result_t) if result_t else 60 * 60
    return round((60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5, 2)

def get_earning(courier):
    coefficient = {
        'foot': 2,
        'bike': 5,
        'car': 9
    }
    total = 0
    assigns = Assign.objects.filter(is_complete=True,
                                    courier_id=courier.courier_id)
    for assign in assigns:
        types_courier_in_assign = defaultdict(int)
        for order in assign.orders.all():
            courier_type = order.courier_type
            types_courier_in_assign[courier_type] += 1
        if len(types_courier_in_assign) == 1:
            total += 500 * coefficient[list(types_courier_in_assign.keys())[0]]
        else:
            coefficients = []
            for key, val in types_courier_in_assign.items():
                coefficients.append(coefficient[key] * val)
            avg_coeficient = sum(coefficients) / sum(types_courier_in_assign.values())
            total += 500 * avg_coeficient
    return int(total)
