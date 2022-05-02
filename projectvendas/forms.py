from django import forms
from .models import Order
from datetime import datetime


class dateinput(forms.DateTimeInput):
    input_type = 'datetime-local'


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['date', 'value', 'quantity', 'status']

        widgets = {'date': dateinput(format="%Y-%m-%dT%H:%M")}
