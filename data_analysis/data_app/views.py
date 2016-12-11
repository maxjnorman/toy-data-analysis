from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count

from .models import Account, Transaction
from .forms import AccountCreateForm, AccountEditForm, TransactionInputForm


def account_list(request):
    accounts = Account.objects.all()
    return render(request, 'budget_app/account_list.html', {'accounts': accounts})


def account_detail(request, pk):
    # Access the database
    account = get_object_or_404(Account, pk=pk)
    transaction_set = Transaction.objects.filter(account__pk=pk).order_by('-trans_date')
    # See if any transactions are new --> balance.check == Null
    if transaction_set.exists():
        null_balance_set = transaction_set.filter(balance__isnull=True)
        if null_balance_set.exists():
            pass
        else:
            null_balance_set = None
    else:
        null_balance_set = None
    # Recalculate the balance values if any are detected as 'new'
    if null_balance_set:
        # Calculate the current balance
        net_input_sum = transaction_set.aggregate(current_balance=Sum('net_input'))
        current_balance = net_input_sum['current_balance']
        account.current_balance = current_balance
        account.save()
        # Find the oldest 'Null' transaction
        first_null_transaction = null_balance_set.first()
        first_null_date = first_null_transaction.trans_date
        for transaction in transaction_set.filter(trans_date__gte=first_null_date):
            transaction.balance = current_balance
            current_balance = current_balance - transaction.net_input
            transaction.save()
    return render(request, 'budget_app/account_detail.html', {'account': account, 'transaction_set': transaction_set})


def account_create(request):
    if request.method == "POST":
        form = AccountCreateForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.published_date = timezone.now()
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
            account.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form = AccountEditForm(instance=account)
    return render(request, 'budget_app/account_edit.html', {'form': form})


def transaction_input(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        form = TransactionInputForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = account
            transaction.nulls_to_zero()
            transaction.calc_net_input()
            transaction.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form = TransactionInputForm()
    return render(request, 'budget_app/transaction_input.html', {'form': form, 'account': account})


def transaction_edit(request, pk):
    # code to edit a transaction entry
    return ("transaction_edit_render")
