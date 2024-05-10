from django import forms

class DateRangeForm(forms.Form):
    start_date = forms.DateField(label='from_date', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='until_date', widget=forms.DateInput(attrs={'type': 'date'}))

class DeliveryTypesForm(forms.Form):
    AMBA = forms.BooleanField(required=False)
    INTERIOR = forms.BooleanField(required=False)

class ZonaForm(forms.Form):
    AMBA = forms.BooleanField(required=False)
    INTERIOR = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        AMBA = cleaned_data.get('filter_option1', False)
        INTERIOR = cleaned_data.get('filter_option2', False)

        if AMBA and INTERIOR:
            raise forms.ValidationError("Only one option can be selected")

        return cleaned_data