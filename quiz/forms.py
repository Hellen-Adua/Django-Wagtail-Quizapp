from django import forms

class AnswerForm(forms.Form):
    choice_id = forms.IntegerField(widget=forms.HiddenInput)