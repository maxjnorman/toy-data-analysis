from django.db import models
from django.utils import timezone
from django.db.models.functions import Coalesce




class Account(models.Model):
    account_name = models.CharField(max_length=100)
    initial_balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True, default=0)
    current_balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

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
    net_input = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return '%s %s' % (self.trans_date, self.description)

    def nulls_to_zero(self):
        self.money_in = Coalesce(self.money_in, 0)
        self.money_out = Coalesce(self.money_out, 0)

    def calc_net_input(self):
        self.net_input = self.money_in - self.money_out
