from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count

from .models import Account, Transaction
from .forms import AccountCreateForm, AccountEditForm, TransactionInputForm, TransactionEditForm


def account_list(request):
    accounts = Account.objects.all()
    return render(request, 'budget_app/account_list.html', {'accounts': accounts})


def account_detail(request, pk):
    # Access the database
    account = get_object_or_404(Account, pk=pk)
    transaction_set = Transaction.objects.filter(account__pk=pk).order_by('-trans_date')
    # Check if the whole account needs recalculating
    if account.recalculate_balance == 1:
        if transaction_set.exists():
            # Calculate the current balance
            net_input_sum = transaction_set.aggregate(current_balance=Sum('net_input'))
            current_balance = net_input_sum['current_balance'] + account.initial_balance
            account.current_balance = current_balance
            account.recalculate_balance = False
            account.save()
            # Calculate the balance at each transaction
            for transaction in transaction_set:
                transaction.balance = current_balance
                current_balance = current_balance - transaction.net_input
                transaction.save()
        else:
            account.current_balance = account.initial_balance
            account.save()
    elif transaction_set.exists():
        recalculate_balance_set = transaction_set.filter(recalculate_balance=True)
        if recalculate_balance_set.exists():
            # Calculate the current balance
            net_input_sum = transaction_set.aggregate(current_balance=Sum('net_input'))
            current_balance = net_input_sum['current_balance'] + account.initial_balance
            account.current_balance = current_balance
            account.save()
            # Find the oldest 'Null' transaction
            first_recalculate_transaction = recalculate_balance_set.first()
            first_recalculate_date = first_recalculate_transaction.trans_date
            for transaction in transaction_set.filter(trans_date__gte=first_recalculate_date):
                transaction.balance = current_balance
                current_balance = current_balance - transaction.net_input
                transaction.recalculate_balance = False
                transaction.save()
        else: pass
    else:
        pass
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
            account.recalculate_balance = True
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
    transaction = get_object_or_404(Transaction, pk=pk)
    account = transaction.account
    if request.method == "POST":
        form = TransactionEditForm(request.POST, instance=transaction)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.nulls_to_zero()
            transaction.calc_net_input()
            transaction.recalculate_balance = True
            transaction.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form = TransactionEditForm(instance=transaction)
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
