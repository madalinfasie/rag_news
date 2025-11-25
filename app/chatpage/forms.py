from django import forms


class ChatForm(forms.Form):
    query = forms.CharField(
        label="Your query",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 1}),
    )
