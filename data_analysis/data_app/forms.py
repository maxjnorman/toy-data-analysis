from django import forms
from .models import Table, TableEntry

class NewTableForm(forms.ModelForm):

    class Meta:
        model = Table
        fields = ('title', 'x_heading', 'y_heading', 'number_of_rows',)

class EditTableForm(forms.ModelForm):

    class Meta:
        model = Table
        fields = ('title', 'x_heading', 'y_heading',)

class TableEntryForm(forms.ModelForm):

    class Meta:
        model = TableEntry
        fields = ('x_value', 'y_value',)
