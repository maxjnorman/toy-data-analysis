from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils import timezone

from .models import Upload, UploadForm
from data_app.models import Account, Year, Month, Transaction
from .functions import build_transaction_dataframe
from data_app.functions import get_month_name, calc_net_input

import pandas as pd
import numpy as np
from datetime import datetime, date
from decimal import Decimal

def upload_file(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method=="POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            data_file = form.save(commit=False)
            data_file.account = account
            data_file.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form=UploadForm()
    files=Upload.objects.all()
    return render(request, 'uploader/upload_file.html', {'form':form, 'files':files})


def delete_file(request, pk):
    data_file = get_object_or_404(Upload, pk=pk)
    account = data_file.account
    data_file.delete()
    return redirect('account_detail', pk=account.pk)


def populate_fields(request, pk):
    upload = get_object_or_404(Upload, pk=pk)
    account = upload.account
    file_location = upload.docfile.path
    data_frame, unique_months = build_transaction_dataframe(file_location, 0)   # Note: functions.py
    transaction_frames = [
        data_frame[data_frame['month_dates']==month_date]
        for month_date
        in unique_months
    ]
    zipped_months = zip(unique_months, transaction_frames)
    for month_tuple in zipped_months:
        month_query = Month.objects.filter(
            account__pk=account.pk,
            month_date__gte=account.start_date.replace(day=1),
            month_date=month_tuple[0]
        )[:1]
        flag = True
        if month_query.exists():
            month = month_query[0]
        elif (month_tuple[0].to_datetime().date()
            >= account.start_date.replace(day=1)):
            month = Month(
                account=account,
                year=account.years.get(year=month_tuple[0].year),
                month_date=month_tuple[0],
                month_name=get_month_name(month_tuple[0].month),
            )
            month.remove_nulls()
            month.save()
        else:
            flag=False
        if flag is True:
            transaction_list = []
            for n in range(0, month_tuple[1].shape[0]):
                transaction = Transaction(
                    account=account,
                    year=month.year,
                    month=month,
                    trans_date=month_tuple[1]['trans_date'].iloc[n],
                    description=str(month_tuple[1]['description'].iloc[n]),
                    id_description=str(month_tuple[1]['description'].iloc[n]),
                    id_balance=np.asscalar(month_tuple[1]['balance'].iloc[n]),
                    money_in=np.asscalar(month_tuple[1]['money_in'].iloc[n]),
                    money_out=np.asscalar(month_tuple[1]['money_out'].iloc[n]),
                    net_input=np.asscalar(month_tuple[1]['net_input'].iloc[n]),
                )
                transaction.remove_nulls()
                transaction_list.append(transaction)
            Transaction.objects.bulk_create(transaction_list)
            valid_transactions = Transaction.objects.filter(
                month__pk=month.pk,
                trans_date__gte=account.start_date,
            )
            net_input_sum = calc_net_input(valid_transactions)
            month.net_input += net_input_sum
            month.save()
        else:
            pass
    return redirect('account_detail', pk=account.pk)


# Note: will now need three of these views. App shouldn't populte across the
# whole year if invoked at the month level, etc...
def populate_fields_old(request, pk):
    uploaded_file = get_object_or_404(Upload, pk=pk)
    account = uploaded_file.account
    file_location = uploaded_file.docfile.path
    data_frame = pd.read_excel(file_location)
    data_frame.columns = ['trans_date', 'description', 'money_in', 'money_out', 'balance']
    data_frame = data_frame.round(2)
    number_of_rows = data_frame.shape[0]
    transaction_list = []
    for n in np.arange(0, number_of_rows):
        trans_date = str(data_frame['trans_date'].iloc[n])[0:10]
        description = str(data_frame['description'].iloc[n])
        money_in = np.asscalar(data_frame['money_in'].iloc[n])
        money_out = np.asscalar(data_frame['money_out'].iloc[n])
        balance = np.asscalar(data_frame['balance'].iloc[n])
        transaction = Transaction(
            account=account,
            trans_date=trans_date,
            description=description,
            money_in=money_in,
            money_out=money_out,
            balance=balance,
            recalculate_balance=True
        )
        transaction.nulls_to_zero()
        transaction.calc_net_input()
        transaction_list.append(transaction)
        # Note: below is not really satisfactory
        # needs to be done to reduce number of SQL objects
        if n % 50 == 0 or n == number_of_rows - 1:
            Transaction.objects.bulk_create(transaction_list)
            transaction_list = []
        else:
            pass
    account.recalculate_balance = True
    account.save()
    return redirect('account_detail', pk=account.pk)
