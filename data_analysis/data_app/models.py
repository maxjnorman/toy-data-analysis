from django.db import models
from django.utils import timezone

class Table(models.Model):
    title = models.CharField(max_length=200)
    x_heading = models.CharField(max_length=200)
    y_heading = models.CharField(max_length=200)
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    number_of_rows = models.IntegerField()

    def __str__(self):
        return self.title

class TableEntry(models.Model):
    table = models.ForeignKey('data_app.Table', related_name='entries')
    x_value = models.FloatField(null=True)
    y_value = models.FloatField(null=True)

    def __str__(self):
        return self.x_value, self.y_value
