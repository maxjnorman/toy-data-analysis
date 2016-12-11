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
        return '%s %s' % (self.x_value, self.y_value)

class Account(models.Model):
    name = models.CharField(max_length=100)

    heading_date = models.CharField(max_length=50)
    heading_description = models.CharField(max_length=50)
    heading_in = models.CharField(max_length=50)
    heading_out = models.CharField(max_length=50)
    heading_balance = models.CharField(max_length=50)

    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.account_name

class Transaction(models.Model):
    table = models.ForeignKey('data_app.Account', related_name='transactions')

    trans_date = models.DateField()
    description = models.CharField(max_length=200)
    money_in = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    money_out = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return '%s %s' % (self.trans_date, self.description)
