from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import Coalesce

from uploader.models import Upload
from .functions import get_month_name

from datetime import datetime, date, timedelta
from calendar import monthrange

class Account(models.Model):
    account_name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, blank=True, null=True)
    created_date = models.DateTimeField(default=timezone.now)
    start_date = models.DateTimeField(default=timezone.now)
    initial_balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=False, default=0)
    # Note: might be best to keep these headings around to display at all
    # levels; year, month, etc...
    heading_date = models.CharField(max_length=50, default="Date")
    heading_description = models.CharField(max_length=50, default="Description")
    heading_in = models.CharField(max_length=50, default="Money In")
    heading_out = models.CharField(max_length=50, default="Money Out")
    heading_balance = models.CharField(max_length=50, default="Balance")

    def __str__(self):
        return self.account_name

    def create_current_year(self):
        current_year = timezone.now().year
        year_obj = Year.objects.filter(account__pk=self.pk, year=current_year)
        if year_obj.exists():
            pass
        else:
            year_obj = Year.objects.create(
                account=self,
                year=current_year,
            )

    def create_missing_years(self):
        current_year = timezone.now().year
        database_year_set = set(Year.objects.filter(account__pk=self.pk).values_list('year', flat=True))
        year_set = set(range(self.start_date.year, current_year + 1))
        if database_year_set == year_set:
            pass
        else:
            missing_years = year_set.difference(database_year_set)
            for n in missing_years:
                Year.objects.get_or_create(
                    account=self,
                    year=n,
                )




class Year(models.Model):
    account = models.ForeignKey('data_app.Account', related_name='years')
    year = models.IntegerField() # Note: can input invalid years. Needs to be 4 digits.
    #year = models.DateTimeField()
    #initial_balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    #net_input = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    #balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return '%s %s' % (self.account, self.year)

    def get_create_month_set(self):
        current_year = timezone.now().year
        current_month = timezone.now().month
        current_months = Month.objects.filter(
            year__pk=self.pk,
            month_date__gte=self.account.start_date,
        ).values_list('month_date', flat=True)
        if self.account.start_date.year < current_year:
            start_month = 1
        else:
            start_month = self.account.start_date.month
        current_month_list = []
        for month_date in current_months:
            current_month_list.append(month_date.month)
        if self.year == current_year:
            month_list = list(range(start_month, current_month + 1)) #list from Jan to 'today'
        else:
            month_list = list(range(start_month, 13)) #list of all months in some past year
        if set(month_list) == set(current_month_list):
            pass
        else:
            missing_months = list(set(month_list).difference(set(current_month_list)))
            for n in missing_months:
                new_month = Month(
                    account=self.account,
                    year=self,
                    month_date = date(self.year, n, 1),    # Note: year is an int
                    month_name=get_month_name(n),
                )
                new_month.remove_nulls()
                new_month.save()
        months = Month.objects.filter(
            year__pk=self.pk,
            month_date__gte=self.account.start_date,
        ).order_by('-month_date')
        return months




class Month(models.Model):
    account = models.ForeignKey('data_app.Account', related_name='months')
    year = models.ForeignKey('data_app.Year', related_name='months')
    #month = models.IntegerField() # Note: can input invalid months
    month_date = models.DateTimeField()
    month_name = models.CharField(max_length=15)
    #initial_balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    net_input = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # Note: can calc balance from net_inputs instead
    #balance = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)    # Note: balace is a database entry so that if can be accessed from Year objects.

    def __str__(self):
        return '%s %s' % (self.month_name)

    def remove_nulls(self):
        self.net_input = Coalesce(self.net_input, 0)

    def set_month_name(self):  # Note: not used yet.
        month_name = get_month_name(self.month_date.month)
        if self.month_name == month_name:
            pass
        else:
            self.month_name = month_name

    #takes in a month object and returns the two adjacent months
    def get_adjacent_months(self, month_object): # Note: used at the month_detail level
        month_date = month_object.month_date
        end_day = monthrange(month_date.year, month_date.month)[1]
        prev_month_date = date(month_date.year, month_date.month, 1) - timedelta(days=1)
        next_month_date = date(month_date.year, month_date.month, end_day) + timedelta(days=1)
        date_list = [prev_month_date, next_month_date]
        for month_date in date_list:
            month_date = month_date.replace(day=1)
        month_list = Month.objects.filter(month_date__in=date_list).order_by('month_date')
        return month_list




class Transaction(models.Model):
    account = models.ForeignKey('data_app.Account', related_name='transactions')
    year = models.ForeignKey('data_app.Year', related_name='transactions')
    month = models.ForeignKey('data_app.Month', related_name='transactions')
    trans_date = models.DateField()
    description = models.CharField(max_length=250)
    id_description = models.CharField(max_length=250)   # Note: used to label transactions --> description from Santander excel file
    money_in = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    money_out = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    net_input = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    # Note: maybe add some BooleanFields for 'Expected' or 'Regular Transaction'.
    # to make the budgeting stuff work.

    def __str__(self):
        return '%s %s' % (self.trans_date, self.description)

    def set_id_description(self):   # Note: adding this as a default to id_description casues migration errors
        self.id_description = self.description

    def calc_net_input(self):
        self.money_in = Coalesce(self.money_in, 0)
        self.money_out = Coalesce(self.money_out, 0)
        self.net_input = self.money_in - self.money_out
