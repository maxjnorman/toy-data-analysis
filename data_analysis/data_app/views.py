from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count

from .models import Account, Year, Month, Transaction
from uploader.models import Upload
from .forms import AccountCreateForm, AccountEditForm, TransactionForm
from .functions import calc_net_input, get_net_inputs

from datetime import datetime, date

def account_list(request):
    accounts = Account.objects.all()    # Note: should add a way to calculate the balances here. Take code from account_detail?
    return render(
        request,
        'budget_app/account_list.html',
        {'accounts': accounts},
    )


def account_detail(request, pk):    # Note: should maybe be using if request.method == 'POST' or maybe 'GET':?
    account = get_object_or_404(Account, pk=pk)
    uploads = Upload.objects.filter(account__pk=account.pk).order_by('-upload_date')
    account.create_current_year()   # Note: create_current_year() ensures that at least the current year is present in year_set below.
    account.create_missing_years()
    years = Year.objects.filter(account__pk=account.pk).order_by('-year') # Note: 'account.years.all()' is this more tidy?
    months = Month.objects.filter(
        account__pk=account.pk,
        month_date__year__lte=timezone.now().year,
        month_date__gte=account.start_date,
    ) # Note: should use 'month_set' instead of year_set for account_balance in case we skip from Month to Account when using app
    net_input = calc_net_input(months) # Note: functions.py
    account_balance = account.initial_balance + net_input   # Note: account balance is not used at a higher level so it is not being stored in the database.
    return render(
        request,
        'budget_app/account_detail.html',
        {'account': account,
        'years': years,
        'uploads': uploads,
        'account_balance': account_balance,},
    )


def year_detail(request, pk):
    year = get_object_or_404(Year, pk=pk)
    account = year.account
    uploads = Upload.objects.filter(account__pk=account.pk).order_by('-upload_date')
    months = year.get_create_month_set()
    net_input_sum = calc_net_input(months)  # Note: functions.py
    balance_months = Month.objects.filter(
        account__pk=account.pk,
        month_date__year__lte=year.year,
        month_date__gte=account.start_date,
    )
    balance_net_input = calc_net_input(months)
    account_balance = account.initial_balance + balance_net_input
    return render(
        request,
        'budget_app/year_detail.html',
        {'account': account,
        'year': year,
        'months': months,
        'uploads': uploads,
        'account_balance': account_balance,},
    )


def month_detail(request, pk):
    month = get_object_or_404(Month, pk=pk)
    year = month.year
    account = year.account  # Note: is 'account' needed?
    transactions = Transaction.objects.filter(
        month__pk=month.pk,
        trans_date__lte=date.today(),
        trans_date__gte=account.start_date,
    ).order_by('-trans_date')
    uploads = Upload.objects.filter(account__pk=account.pk).order_by('-upload_date')
    # Note: update the selected month's net input
    net_input = calc_net_input(transactions) # Note: functions.py
    if (month.net_input == net_input):    # Note: need to ensure the Month.net_input is always saved if it changes
        pass
    else:
        month.net_input = net_input
        month.save()    # Note: only save if there is a reason to
    # Note: get the previous months and calc the net input
    prev_months = Month.objects.filter(
        year__pk=year.pk,
        month_date__lte=month.month_date,
        month_date__gte=account.start_date,
    )
    current_balance = calc_net_input(prev_months) + account.initial_balance
    month_balance = current_balance
    balance_list = []   # will need to loop over the net_input_list and append the resulting balance to balance_list
    for transaction in transactions:
        balance_list.append(month_balance)
        month_balance -= transaction.net_input
    zipped_transactions = zip(transactions, balance_list)
    #adjacent_months = month.get_adjacent_months(month)    # Note: need to get the previous and next month from the database here not in the template.
    return render(
        request,
        'budget_app/month_detail.html',
        {'account': account,
        'year': year,
        'month': month,
        'current_balance': current_balance,
        'zipper_transactions': zipped_transactions,
        #'adjacent_months': adjacent_months,
        'uploads': uploads,},
    )


def account_create(request):
    if request.method == "POST":
        form = AccountCreateForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            #account.published_date = timezone.now()
            account.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form = AccountCreateForm()
    return render(request, 'budget_app/account_create.html', {'form': form})


def account_edit(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        form = AccountEditForm(request.POST, instance=account)
        if form.is_valid():
            account = form.save(commit=False)
            account.recalculate_balance = True
            account.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form = AccountEditForm(instance=account)
    return render(request, 'budget_app/account_edit.html', {'form': form})


def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    transaction_set = Transaction.objects.filter(account__pk=account.pk)
    upload_set = Upload.objects.filter(account__pk=account.pk)
    for data_file in upload_set:
        data_file.delete()
    for transaction in transaction_set:
        transaction.delete()
    account.delete()
    return redirect(account_list)


def clear_transactions(request, pk):
    account = get_object_or_404(Account, pk=pk)
    transaction_set = account.get_transaction_set()
    transaction_set.delete()
    return redirect(account_detail, pk=account.pk)


#def recalculate_account(request, pk):
#    account = get_object_or_404(Account, pk=pk)
#    account.recalculate_balance=True
#    account.save()
#    return redirect(account_detail, pk=account.pk)


def transaction_input(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = account
            #transaction.nulls_to_zero()
            transaction.calc_net_input()
            #transaction.recalculate_balance=True
            transaction.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form = TransactionForm()
    return render(request, 'budget_app/transaction_input.html', {'form': form, 'account': account})


def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    account = transaction.account
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.nulls_to_zero()
            transaction.calc_net_input()
            transaction.recalculate_balance = True
            transaction.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'budget_app/transaction_edit.html', {'form': form, 'account': account})


def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    account = transaction.account
    transaction_date = transaction.trans_date
    transaction_set = Transaction.objects.filter(trans_date__gte=transaction_date)
    transaction.delete()
    if transaction_set.exists():
        for transaction in transaction_set:
            transaction.recalculate_balance = True
            transaction.save()
    else:
        pass
    return account_detail(request, pk=account.pk)
