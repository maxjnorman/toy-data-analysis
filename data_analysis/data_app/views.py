from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Table, TableEntry
from .forms import NewTableForm, EditTableForm, TableEntryForm


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
