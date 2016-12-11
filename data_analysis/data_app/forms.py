from django import forms

from .models import Account, Transaction

class AccountCreateForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = (
            'account_name',
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
            'account_name',
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
        )

class TransactionEditForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = (
            'trans_date',
            'description',
            'money_in',
            'money_out',
        )
