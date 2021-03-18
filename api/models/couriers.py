from django.contrib.postgres.fields import ArrayField
from django.db import models


class Courier(models.Model):
    courier_id = models.PositiveIntegerField(primary_key=True)
    courier_type = models.CharField(
        max_length=4,
        verbose_name='Courier type',
        blank=False,
    )
    regions = ArrayField(models.CharField(max_length=200), blank=False)
    working_hours = ArrayField(models.CharField(max_length=200), blank=False)
