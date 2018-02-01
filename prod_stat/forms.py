from django import forms

class LoginForm(forms.Form):
    user_name = forms.CharField(label='Ключ', max_length=40,
                                widget=forms.TextInput(attrs={'class': 'col-12 form-control'}))
    user_pass = forms.CharField(label='Секрет', max_length=40,
                                widget=forms.PasswordInput(attrs={'class': 'col-12 form-control'}))