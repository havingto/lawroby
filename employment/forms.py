from django import forms
from employment.models import Question, Choice

class Question_form(forms.Form):
    choice_list=forms.ChoiceField(
        choices = choices,
        widget=forms.
