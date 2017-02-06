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
    created_date = models.DateField(default=timezone.now)
    start_date = models.DateField(default=timezone.now)
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

    def create_year_set(self):
        database_year_set = set(Year.objects.filter(
            account__pk=self.pk,
            year__gte=self.start_date.year,
            year__lte=timezone.now().year
        ).values_list('year', flat=True))
        year_set = set(range(self.start_date.year, timezone.now().year + 1))
        if database_year_set == year_set:
            pass
        else:
            missing_years = year_set.difference(database_year_set)
            new_years = []
            for n in missing_years:
                new_year = Year(
                    account=self,
                    year=n,
                )
                new_years.append(new_year)
            Year.objects.bulk_create(new_years)




class Year(models.Model):
    account = models.ForeignKey('data_app.Account', related_name='years')
    year = models.IntegerField() # Note: can input invalid years. Needs to be 4 digits.

    def __str__(self):
        return '%s %s' % (self.account, self.year)

    def get_create_month_set(self):
        # Note: needs a total rewrite...
        if self.year > self.account.start_date.year:
            start_month = 1
        else:
            start_month = self.account.start_date.month
        if self.year < timezone.now().year:
            end_month = 12
        else:
            end_month = timezone.now().month
        month_list = list(range(start_month, end_month + 1))
        database_months = Month.objects.filter(
            year__pk=self.pk,
        ).values_list('month_date', flat=True)
        database_month_list = []
        for month_date in database_months:
            database_month_list.append(month_date.month)
        if set(database_month_list) == set(month_list):
            pass
        else:
            missing_months = set(month_list).difference(set(database_month_list))
            new_months = []
            for n in missing_months:
                new_month = Month(
                    account=self.account,
                    year=self,
                    month_date = date(self.year, n, 1),    # Note: year is an int
                    month_name=get_month_name(n),
                )
                new_month.remove_nulls()
                new_months.append(new_month)
            Month.objects.bulk_create(new_months)
        months = Month.objects.filter(
            year__pk=self.pk,
            month_date__month__gte=start_month,
            month_date__month__lte=end_month,
        ).order_by('-month_date')
        return months




class Month(models.Model):
    account = models.ForeignKey('data_app.Account', related_name='months')
    year = models.ForeignKey('data_app.Year', related_name='months')
    month_date = models.DateField()
    month_name = models.CharField(max_length=15)
    net_input = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)  # Note: can calc balance from net_inputs

    def __str__(self):
        return '%s %s' % (self.month_name)

    def remove_nulls(self):
        self.net_input = Coalesce(self.net_input, 0)

    def set_month_name(self):
        month_name = get_month_name(self.month_date.month)
        if self.month_name == month_name:
            pass
        else:
            self.month_name = month_name

    # Note: not used yet
    # Note: takes in a month object and returns the two adjacent months
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
