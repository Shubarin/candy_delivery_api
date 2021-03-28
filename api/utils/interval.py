import datetime as dt
from typing import List, Tuple

from rest_framework.exceptions import ValidationError


class Interval:
    def __init__(self):
        self.working_hours = None
        self.delivery_hours = None

    @staticmethod
    def convert_str_to_time(intervals: List[str]) -> List[dt.datetime]:
        result = []
        for interval in intervals:
            try:
                start, end = Interval.parse_interval(interval)
                result.append({'start': start, 'end': end})
            except ValueError:
                raise ValidationError('invalid values in intervals list')
        return result

    def set_working_hours(self, intervals: List[str]) -> None:
        self.working_hours = self.convert_str_to_time(intervals)

    def set_delivery_hours(self, intervals: List[str]) -> None:
        self.delivery_hours = self.convert_str_to_time(intervals)

    def delivery_allowed(self) -> bool:
        if self.working_hours and self.delivery_hours:
            for delivery_hour in self.delivery_hours:
                for working_hour in self.working_hours:
                    if self.is_intervals_intersection(delivery_hour,
                                                      working_hour):
                        return True
        return False

    @staticmethod
    def is_intervals_intersection(a, b) -> bool:
        return a['start'] <= b['end'] and a['end'] >= b['start']

    @staticmethod
    def parse_interval(period) -> Tuple[dt.datetime, dt.datetime]:
        start, end = period.split('-')
        start = dt.datetime.strptime(start, '%H:%M')
        end = dt.datetime.strptime(end, '%H:%M')
        return start, end
