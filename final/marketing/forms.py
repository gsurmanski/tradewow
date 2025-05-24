# myapp/forms.py

from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your username'
        })
    )
    
    password = forms.CharField(
        label="Password",
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your password'
        })
    )

class RegisterForm(forms.Form):
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form_input',
            'placeholder': 'Pick your username'
        })
    )
    
    email = forms.EmailField(
        label="Email",
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form_input',
            'placeholder': 'Enter your Email'
        })
    )

    password = forms.CharField(
        label="Password",
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'class': 'form_input',
            'placeholder': 'Pick your password'
        })
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'class': 'form_input',
            'placeholder': 'Confirm your password'
        })
    )
