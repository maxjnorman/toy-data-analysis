from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count

from .models import Account, Year, Month, Transaction
from uploader.models import Upload
from .forms import AccountCreateForm, AccountEditForm, TransactionForm, TransactionFormAccount, TransactionFormYear, TransactionFormMonth
from .functions import calc_net_input, get_net_inputs, get_month_name

from datetime import datetime, date

def account_list(request):
    accounts = Account.objects.all()
    balance_list = []
    for account in accounts:
        months = Month.objects.filter(
            account__pk=account.pk,
            month_date__gte=account.start_date.replace(day=1),
        )
        balance = calc_net_input(months) + account.initial_balance
        balance_list.append(balance)
    zipped_accounts = zip(accounts, balance_list)
    return render(
        request,
        'budget_app/account_list.html',
        {'zipped_accounts': zipped_accounts},
    )


def account_detail(request, pk):    # Note: should maybe be using if request.method == 'POST' or maybe 'GET':?
    account = get_object_or_404(Account, pk=pk)
    uploads = account.uploads.order_by('-upload_date')
    account.create_year_set()   # Note: fills in any 'missing' years
    years = account.years.filter(
        year__gte=account.start_date.year,
        year__lte=timezone.now().year,
    ).order_by('-year')
    months = Month.objects.filter(
        account__pk=account.pk,
        month_date__year__lte=timezone.now().year,
    ) # Note: should use 'month_set' instead of year_set for account_balance in case we skip from Month to Account when using app
    year_balances = []
    for year in years:
        year_months = months.filter(
            month_date__year__lte=year.year
        )
        net_input = calc_net_input(year_months) + account.initial_balance
        year_balances.append(net_input)
    zipped_years = zip(years, year_balances)
    net_input = calc_net_input(months) # Note: functions.py
    account_balance = account.initial_balance + net_input   # Note: account balance is not used at a higher level so it is not being stored in the database.
    return render(
        request,
        'budget_app/account_detail.html',
        {'account': account,
        'zipped_years': zipped_years,
        'uploads': uploads,
        'account_balance': account_balance,},
    )


def year_detail(request, pk):
    year = get_object_or_404(Year, pk=pk)
    account = year.account
    uploads = account.uploads.order_by('-upload_date')
    months = year.get_create_month_set()
    balance_months = Month.objects.filter(
        account__pk=account.pk,
        month_date__year__lte=year.year,
    )
    net_input_sum = calc_net_input(balance_months)
    account_balance = account.initial_balance + net_input_sum
    month_net_inputs = get_net_inputs(months)   # Note: returns a list of net inputs
    var_account_balance = account_balance
    month_balance_list = []
    for month in months:
        month_balance_list.append(var_account_balance)
        var_account_balance -= month.net_input
    zipped_months = zip(months, month_balance_list)
    return render(
        request,
        'budget_app/year_detail.html',
        {'account': account,
        'year': year,
        'zipped_months': zipped_months,
        'uploads': uploads,
        'account_balance': account_balance,},
    )


def month_detail(request, pk):
    month = get_object_or_404(Month, pk=pk)
    year = month.year
    account = year.account
    transactions = Transaction.objects.filter(
        month__pk=month.pk,
        trans_date__lte=timezone.now(),
        trans_date__gte=account.start_date,
    ).order_by('-trans_date')
    uploads = account.uploads.order_by('-upload_date')
    net_input = calc_net_input(transactions) # Note: functions.py
    if (month.net_input == net_input):
        pass
    else:
        month.net_input = net_input
        month.save()
    prev_months = Month.objects.filter(
        account__pk=account.pk,
        month_date__lt=month.month_date,
        month_date__month__gte=account.start_date.month,
    )
    current_balance = calc_net_input(prev_months) + account.initial_balance + net_input
    var_balance = current_balance
    balance_list = []
    for transaction in transactions:
        balance_list.append(var_balance)
        var_balance -= transaction.net_input
    zipped_transactions = zip(transactions, balance_list)
    #adjacent_months = month.get_adjacent_months(month)    # Note: would need to get the previous and next month from the database here, not in the template.
    return render(
        request,
        'budget_app/month_detail.html',
        {'account': account,
        'year': year,
        'month': month,
        'current_balance': current_balance,
        'month_balance': month.net_input,
        'zipped_transactions': zipped_transactions,
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
            oldest_month = Month.objects.filter(
                account__pk=account.pk,
                month_date__month__gte=account.start_date.month,
            ).order_by('month_date')[0]
            transactions = Transaction.objects.filter(
                month__pk=oldest_month.pk,
                trans_date__gte=account.start_date,
            )
            net_input = calc_net_input(transactions)
            oldest_month.net_input = net_input
            oldest_month.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form = AccountEditForm(instance=account)
    return render(request, 'budget_app/account_edit.html', {'form': form})


def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    uploads = account.uploads.all()
    uploads.delete()
    years = account.years.all()
    years.delete()
    months = account.months.all()
    months.delete()
    transactions = account.transactions.all()
    transactions.delete()
    account.delete()
    return redirect(account_list)


def transaction_input_account(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        form = TransactionFormAccount(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            year_query = Year.objects.filter(
                account__pk=account.pk,
                year=transaction.trans_date.year,
            )
            month_query = Month.objects.filter(
                account__pk=account.pk,
                month_date__year=transaction.trans_date.year,
                month_date__month=transaction.trans_date.month
            )
            if year_query.exists() and month_query.exists():
                year = year_query[0]
                month = month_query[0]
                transaction.account = account
                transaction.year = year
                transaction.month = month
                transaction.set_id_description()
                transaction.calc_net_input()
                transaction.save()
                if transaction.net_input == 0:
                    pass
                else:
                    month.net_input += transaction.net_input
                    month.save()
                return redirect('account_detail', pk=account.pk)
            else:
                form = TransactionForm()
        else:
            form = TransactionForm()
    else:
        form = TransactionForm()
    return render(
        request,
        'budget_app/transaction_input.html',
        {'form': form,
        'account': account,},
    )


def transaction_input_year(request, pk):
    year = get_object_or_404(Year, pk=pk)
    account = year.account
    if request.method == "POST":
        form = TransactionFormYear(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            month_query = Month.objects.filter(
                account__pk=account.pk,
                month_date__year=transaction.trans_date.year,
                month_date__month=transaction.trans_date.month
            )
            if month_query.exists():
                month = month_query[0]
                transaction.account = account
                transaction.year = year
                transaction.month = month
                transaction.set_id_description()
                transaction.calc_net_input()
                transaction.save()
                if transaction.net_input == 0:
                    pass
                else:
                    month.net_input += transaction.net_input
                    month.save()
                return redirect('year_detail', pk=year.pk)
            else:
                form = TransactionForm()
        else:
            form = TransactionForm()
    else:
        form = TransactionForm()
    return render(
        request,
        'budget_app/transaction_input.html',
        {'form': form,
        'account': account,
        'year': year,},
    )


def transaction_input_month(request, pk):
    month = get_object_or_404(Month, pk=pk)
    year = month.year
    account = month.account
    if request.method == "POST":
        form = TransactionFormMonth(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = account
            transaction.year = year
            transaction.month = month
            transaction.set_id_description()
            transaction.calc_net_input()
            transaction.save()
            if transaction.net_input == 0:
                pass
            else:
                month.net_input += transaction.net_input
                month.save()
            return redirect('month_detail', pk=transaction.month.pk)
        else:
            form = TransactionForm()
    else:
        form = TransactionForm()
    return render(
        request,
        'budget_app/transaction_input.html',
        {'form': form,
        'account': account,
        'year': year,
        'month': month,},
    )


def transaction_input(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            year_query = Year.objects.filter(
                account__pk=account.pk,
                year=transaction.trans_date.year,
            )
            month_query = Month.objects.filter(
                account__pk=account.pk,
                month_date__year=transaction.trans_date.year,
                month_date__month=transaction.trans_date.month
            )
            if year_query.exists() and month_query.exists():
                flag = True
                year = year_query[0]
                month = month_query[0]
            elif year_query.exists() and transaction.trans_date >= account.start_date:
                flag = True
                year = year_query[0]
                month = Month(
                    account=account,
                    year=year,
                    month_date = date(year.year, transaction.trans_date.month, 1),    # Note: year is an int
                    month_name=get_month_name(transaction.trans_date.month),
                )
                month.remove_nulls()
                month.save()
            else:
                flag = False
            if flag is True:
                transaction.account = account
                transaction.year = year
                transaction.month = month
                transaction.set_id_description()
                transaction.calc_net_input()
                transaction.save()
                if transaction.net_input == 0:
                    pass
                else:
                    month.net_input += transaction.net_input
                    month.save()
                    return redirect('month_detail', pk=transaction.month.pk)
    else:
        form = TransactionForm()
    return render(
        request,
        'budget_app/transaction_input.html',
        {'form': form,
        'account': account})


# Note: if changing month date, transaction doesn't move to new month. Need to rewrite.
def transaction_edit(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    account = transaction.account
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.calc_net_input()
            transaction.save()
            return redirect('month_detail', pk=transaction.month.pk)
    else:
        form = TransactionForm(instance=transaction)
    return render(request, 'budget_app/transaction_edit.html', {'form': form, 'account': account})


def transaction_delete(request, pk):    # Note: only accessed at month_detail level
    transaction = get_object_or_404(Transaction, pk=pk)
    month = transaction.month
    transaction.delete()
    return month_detail(request, pk=month.pk)


def clear_transactions(request, pk):
    account = get_object_or_404(Account, pk=pk)
    transactions = account.transactions.all()
    transactions.delete()
    return redirect(account_detail, pk=account.pk)


def recalculate_account(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.recalculate_balance=True
    account.save()
    return redirect(account_detail, pk=account.pk)
