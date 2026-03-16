from django import forms
from .models import Expense, CATEGORY_CHOICES
import datetime


class ExpenseForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=datetime.date.today
    )

    class Meta:
        model = Expense
        fields = ['description', 'amount', 'date', 'category', 'notes']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Swiggy dinner order'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional notes...'}),
        }


class FilterForm(forms.Form):
    FILTER_CHOICES = [
        ('all', 'All Time'),
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
    ]
    filter = forms.ChoiceField(choices=FILTER_CHOICES, required=False,
                               widget=forms.Select(attrs={'class': 'form-control'}))
    search = forms.CharField(required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search...'}))
