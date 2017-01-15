from django import forms

from .models import Account, Transaction

class AccountCreateForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = (
            'account_name',
            'initial_balance',
        )


class AccountEditForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = (
            'account_name',
            'heading_date',
            'heading_description',
            'heading_in',
            'heading_out',
            'heading_balance',
            'initial_balance',
        )


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = (
            'trans_date',
            'description',
            'money_in',
            'money_out',
        )
