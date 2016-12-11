from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Account, Transaction
from .forms import AccountCreateForm, AccountEditForm, TransactionInputForm


def account_list(request):
    accounts = Account.objects.all()
    return render(request, 'budget_app/account_list.html', {'accounts' : accounts})

def account_detail(request, pk):
    account = get_object_or_404(Account, pk=pk)
    return render(request, 'budget_app/account_detail.html', {'account' : account})

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
    return render(request, 'budget_app/account_create.html', {'form' : form})

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
    return render(request, 'budget_app/account_edit.html', {'form' : form})

def transaction_input(request, pk):
    account = get_object_or_404(Account, pk=pk)
    if request.method == "POST":
        form = TransactionInputForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.account = account
            transaction.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form = TransactionInputForm()
    return render(request, 'budget_app/transaction_input.html', {'form': form, 'account': account})

def transaction_edit(request, pk):
    # code to edit a transaction entry
    return ("transaction_edit_render")
