from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import Coalesce

from uploader.models import Upload

class Account(models.Model):
    account_name = models.CharField(max_length=100)
    initial_balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=False, default=0)
    current_balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    heading_date = models.CharField(max_length=50, default="Date")
    heading_description = models.CharField(max_length=50, default="Description")
    heading_in = models.CharField(max_length=50, default="Money In")
    heading_out = models.CharField(max_length=50, default="Money Out")
    heading_balance = models.CharField(max_length=50, default="Balance")
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)
    recalculate_balance = models.BooleanField(default=True)

    def __str__(self):
        return self.account_name

    def get_transaction_set(self):
        transaction_set = Transaction.objects.filter(account__pk=self.pk).order_by('-trans_date')
        return transaction_set

    def get_upload_set(self):
        upload_set = Upload.objects.filter(account__pk=self.pk).order_by('-upload_date')
        return upload_set

    def recalculate_transactions_all(self, transaction_set):
        if transaction_set.exists():
            # Calculate the current balance
            net_input_sum = transaction_set.aggregate(current_balance=Sum('net_input'))
            current_balance = net_input_sum['current_balance'] + self.initial_balance
            self.current_balance = current_balance
            self.recalculate_balance = False
            self.save()
            # Calculate the balance at each transaction
            for transaction in transaction_set:
                transaction.balance = current_balance
                current_balance = current_balance - transaction.net_input
                transaction.save()
        else:
            self.current_balance = self.initial_balance
            self.save()

    def recalculate_transactions(self, transaction_set):
        recalculate_balance_set = transaction_set.filter(recalculate_balance=1)
        if recalculate_balance_set.exists():
            # Calculate the current balance
            net_input_sum = transaction_set.aggregate(current_balance=Sum('net_input'))
            current_balance = net_input_sum['current_balance'] + self.initial_balance
            self.current_balance = current_balance
            self.save()
            # Find the oldest incorrect transaction
            first_recalculate_transaction = recalculate_balance_set[0] # Note: order_by('-trans_date') above, hence [0] for oldest
            first_recalculate_date = first_recalculate_transaction.trans_date
            for transaction in transaction_set.filter(trans_date__gte=first_recalculate_date):
                transaction.balance = current_balance
                current_balance = current_balance - transaction.net_input
                transaction.recalculate_balance = False
                transaction.save()
        else:
            pass




class Transaction(models.Model):
    account = models.ForeignKey('data_app.Account', related_name='transactions')
    trans_date = models.DateField()
    description = models.CharField(max_length=200)
    money_in = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    money_out = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    net_input = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    recalculate_balance = models.BooleanField(default=True)

    def __str__(self):
        return '%s %s' % (self.trans_date, self.description)

    def nulls_to_zero(self):
        self.money_in = Coalesce(self.money_in, 0)
        self.money_out = Coalesce(self.money_out, 0)

    def calc_net_input(self):
        self.net_input = self.money_in - self.money_out
