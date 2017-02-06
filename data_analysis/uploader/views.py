from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils import timezone
from django import db

from .models import Upload, UploadForm
from data_app.models import Account, Year, Month, Transaction
from .functions import build_transaction_dataframe
from data_app.functions import get_month_name, calc_net_input, get_net_inputs

import os
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
    return render(
        request,
        'uploader/upload_file.html',
        {'form':form,
        'files':files}
    )


def delete_file(request, pk):
    upload = get_object_or_404(Upload, pk=pk)
    account = upload.account
    file_location = upload.docfile.path
    upload.delete()
    os.remove(file_location)
    return redirect('account_detail', pk=account.pk)


def populate_fields(request, pk):
    upload = get_object_or_404(Upload, pk=pk)
    account = upload.account
    file_location = upload.docfile.path
    data_frame, unique_months = build_transaction_dataframe(file_location, 0)
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
            current_ids = list(month.transactions.all().values_list(
                'trans_date',
                'id_description',
                'id_balance',
                ))

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
                id_tuple = (
                    transaction.trans_date.to_datetime().date(),
                    str(transaction.id_description),
                    str(transaction.id_balance),
                )
                if id_tuple in set(current_ids):
                    pass
                else:
                    transaction_list.append(transaction)
            Transaction.objects.bulk_create(transaction_list)
            valid_transactions = month.transactions.all().filter(
                trans_date__gte=account.start_date,
                trans_date__lte=timezone.now(),
            )
            net_input = calc_net_input(valid_transactions)
            month.net_input = net_input
            month.save()
        else:
            pass
    return redirect('account_detail', pk=account.pk)
