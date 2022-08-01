from django import forms
from .models import *

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["user_id"]

class Geo(forms.Form):
    id_or_phone = forms.CharField(max_length=100, label="Введите id товара или же ваш номер телефона")