from django import forms
from .models import Restaurant, Review

class RestaurantForm(forms.ModelForm):

    class Meta:
        model = Restaurant

        fields = ['name', 'image', 'address', 'cuisine']


class ReviewForm(forms.ModelForm):

    class Meta:

        model = Review

        fields = ['rating', 'comment']