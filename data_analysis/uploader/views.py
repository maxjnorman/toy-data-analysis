from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

from .models import Upload, UploadForm
from data_app.models import Account, Transaction

import pandas as pd
import numpy as np

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
        # Note: below is not really unsatisfactory
        # needs to be done to reduce number of SQL objects
        if n % 50 == 0 or n == number_of_rows - 1:
            Transaction.objects.bulk_create(transaction_list)
            transaction_list = []
        else:
            pass
    account.recalculate_balance = True
    account.save()
    return redirect('account_detail', pk=account.pk)
