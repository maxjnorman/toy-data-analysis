from django.db import models
from django.utils import timezone

class Account(models.Model):
    account_name = models.CharField(max_length=100)
    heading_date = models.CharField(max_length=50, default="Date")
    heading_description = models.CharField(max_length=50, default="Description")
    heading_in = models.CharField(max_length=50, default="Money In")
    heading_out = models.CharField(max_length=50, default="Money Out")
    heading_balance = models.CharField(max_length=50, default="Balance")
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.account_name

class Transaction(models.Model):
    account = models.ForeignKey('data_app.Account', related_name='transactions')
    trans_date = models.DateField()
    description = models.CharField(max_length=200)
    money_in = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    money_out = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return '%s %s' % (self.trans_date, self.description)
