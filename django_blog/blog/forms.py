from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Extended user creation form that includes email field
    """
    email = forms.EmailField(
        required=True,
        help_text="Required. Enter a valid email address.",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name (optional)'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name (optional)'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            
        # Update placeholders for default fields
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirm your password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last name'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username field read-only for profile updates
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['username'].help_text = "Username cannot be changed."


class PasswordChangeForm(forms.Form):
    """
    Custom form for changing password with Bootstrap styling
    """
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Current password'
        }),
        help_text="Enter your current password for verification."
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        }),
        help_text="Enter your new password."
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        }),
        help_text="Enter the same password again for verification."
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError("Your current password is incorrect.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise forms.ValidationError("The two password fields didn't match.")
        
        return cleaned_data

    def save(self):
        self.user.set_password(self.cleaned_data['new_password1'])
        self.user.save()
        return self.user