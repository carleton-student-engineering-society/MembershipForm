from django import forms
class MembershipForm(forms.Form):
    name = forms.CharField(
        label="Full Legal Name",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name'
        })
    )
    address = forms.CharField(
        label="Mailing Address",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your mailing address'
        })
    )
    student_number = forms.IntegerField(
        label="Student Number",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your student number'
        })
    )

    program = forms.CharField(
        label="Program",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your program (e.g. Software Engineering)'
        })
    )

    engineer = forms.BooleanField(
        label="Are you an engineering student?",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )