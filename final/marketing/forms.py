# myapp/forms.py

from django import forms
from .models import User

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

class UploadPic(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']
        widgets = {
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form_input'})
        }
    '''
    #add method for cleaning email. use word 'clean' for auto run
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already in use")
        #if no error
        return email
    '''