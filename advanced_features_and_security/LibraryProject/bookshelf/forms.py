from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "publication_year"]
        widgets = {
            "title": forms.TextInput(attrs={"maxlength": 200, "required": True}),
            "author": forms.TextInput(attrs={"maxlength": 100, "required": True}),
            "publication_year": forms.NumberInput(attrs={"min": 0, "max": 9999, "required": True}),
        }

    def clean_publication_year(self):
        year = self.cleaned_data.get("publication_year")
        if year is not None and (year < 0 or year > 9999):
            raise forms.ValidationError("Invalid year.")
        return year


class ExampleForm(forms.Form):
    sample = forms.CharField(max_length=200, required=True)

