from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Table, TableEntry
from .forms import NewTableForm, EditTableForm, TableEntryForm

from .models import Account, Transaction
from .forms import AccountCreateForm, AccountEditForm, TransactionInputForm


def account_list(request):
    accounts = Account.objects.all()
    return render(request, 'budget_app/account_list.html', {'accounts' : accounts})

def account_detail(request, pk):
    accounts = get_object_or_404(Account, pk=pk)
    return render(request, 'budget_app/account_detail.html', {'accounts' : account})

def account_create(request):
    if request.method == "POST":
        form = AccountCreateForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.published_date = timezone.now()
            account.save()
            return redirect('account_detail', pk=account.pk)
    else:
        form = NewTableForm()
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
    account = get_object_or_404(Table, pk=pk)
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




def table_list(request):
    tables = Table.objects.all()
    return render(request, 'data_app/table_list.html', {'tables' : tables})

def table_detail(request, pk):
    table = get_object_or_404(Table, pk=pk)
    return render(request, 'data_app/table_detail.html', {'table' : table})

def create_table(request):
    if request.method == "POST":
        form = NewTableForm(request.POST)
        if form.is_valid():
            table = form.save(commit=False)
            table.published_date = timezone.now()
            table.save()
            return redirect('table_detail', pk=table.pk)
    else:
        form = NewTableForm()
    return render(request, 'data_app/table_create.html', {'form' : form})

def edit_table(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == "POST":
        form = EditTableForm(request.POST, instance=table)
        if form.is_valid():
            table = form.save(commit=False)
            table.published_date = timezone.now()
            table.save()
            return redirect('table_detail', pk=table.pk)
    else:
        form = EditTableForm(instance=table)
    return render(request, 'data_app/table_edit.html', {'form' : form})

def input_table_entry(request, pk):
    table = get_object_or_404(Table, pk=pk)
    if request.method == "POST":
        form = TableEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.table = table
            entry.save()
            return redirect('table_detail', pk=table.pk)
    else:
        form = TableEntryForm()
    return render(request, 'data_app/input_table_entry.html', {'form': form, 'table': table})
