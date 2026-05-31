from django import forms
from .models import MenuItem

class MenuItemForm(forms.ModelForm):

    class Meta:
        model = MenuItem

        fields = [
            'restaurant',
            'name',
            'description',
            'price',
            'image',
            'available'
        ]