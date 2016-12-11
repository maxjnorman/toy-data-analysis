from django import forms

from .models import Table, TableEntry

from .models import Account, Transaction

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


class AccountCreateForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = (
            'name',
            'heading_date',
            'heading_description',
            'heading_in',
            'heading_out',
            'heading_balance',
        )


class AccountEditForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = (
            'name',
            'heading_date',
            'heading_description',
            'heading_in',
            'heading_out',
            'heading_balance',
        )


class TransactionInputForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = (
            'trans_date',
            'description',
            'money_in',
            'money_out',
            'balance',
        )

class TransactionEditForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = (
            'trans_date',
            'description',
            'money_in',
            'money_out',
            'balance',
        )
