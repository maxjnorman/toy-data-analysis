from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models.functions import Coalesce
from django.db.models import Sum, Count

from .models import Account, Transaction
from uploader.models import Upload
from .forms import AccountCreateForm, AccountEditForm, TransactionForm

def account_list(request):
    accounts = Account.objects.all()
    return render(request, 'budget_app/account_list.html', {'accounts': accounts})


def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    transaction_set = account.get_transaction_set()
    upload_set = account.get_upload_set()
    if account.recalculate_balance == 1:
        account.recalculate_transactions_all(transaction_set)
    else:
        account.recalculate_transactions(transaction_set)
    return render(request, 'budget_app/account_detail.html', {'account': account, 'transaction_set': transaction_set, 'upload_set': upload_set})


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


def account_delete(request, pk):
    account = get_object_or_404(Account, pk=pk)
    transaction_set = account.get_transaction_set()
    upload_set = account.get_upload_set()
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
    #for transaction in transaction_set:
        #transaction.delete()
    return redirect(account_detail, pk=account.pk)


def recalculate_account(request, pk):
    account = get_object_or_404(Account, pk=pk)
    account.recalculate_balance=True
    account.save()
    return redirect(account_detail, pk=account.pk)


def transaction_input(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = account
            transaction.nulls_to_zero()
            transaction.calc_net_input()
            transaction.recalculate_balance=True
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
