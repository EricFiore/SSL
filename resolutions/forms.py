import pytz
import datetime
from django import forms
from library.models import ProductModel
from .models import CustomFixes, Error
from tracking.time_modification import convert_to_datetime, convert_to_end_datetime, convert_to_start_datetime
from django_summernote.fields import SummernoteTextFormField, SummernoteTextField


class CalInput(forms.DateInput):
    input_type = 'date'


class StatisticalChoiceForm(forms.Form):
    DEFAULT = 'df'
    HPI = 'HPI'
    TVOT = 'TVOT'
    TABLE_CHOICES = [
        (DEFAULT, 'none'),
        (HPI, 'Highest Percentile Items'),
        (TVOT, 'Total Views Over Time')
    ]
    table = forms.ChoiceField(choices=TABLE_CHOICES)


class MainSearch(forms.Form):
    search = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '2300, MICAS, etc'}),
                             max_length=100)

    def clean_search(self):
        search = [term.strip() for term in self.cleaned_data['search'].split(',')]
        search = [' '.join(word.split()).lower() for word in search]
        return search


class TechTipDailySearch(forms.Form):
    period_start = forms.DateField(widget=CalInput, initial=datetime.datetime.today() - datetime.timedelta(days=5))
    period_end = forms.DateField(widget=CalInput, initial=datetime.datetime.today())

    def clean_period_start(self):
        return convert_to_end_datetime(self.cleaned_data['period_start'])

    def clean_period_end(self):
        return convert_to_end_datetime(self.cleaned_data['period_end'])

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['period_end'] <= cleaned_data['period_start']:
            raise forms.ValidationError('Start Date Must be Before End Date')
        if cleaned_data['period_end'] - cleaned_data['period_start'] >= datetime.timedelta(days=30):
            raise forms.ValidationError('Time Span Must be Less Than 30 Days')
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        if cleaned_data['period_end'] > convert_to_start_datetime(tomorrow):
            raise forms.ValidationError('Do Not Choose a Day Later Than the Current Day')
        return cleaned_data


class TechTipSearch(forms.Form):
    start_date = forms.DateField(widget=CalInput, initial=datetime.datetime.today() - datetime.timedelta(days=30))
    end_date = forms.DateField(widget=CalInput, initial=datetime.datetime.today())
    percentile = forms.ChoiceField(choices=[(90, '10%'), (80, '20%'), (70, '30%'), (60, '40%'), (50, '50%')],
                                   initial=70)

    def clean_start_date(self):
        return convert_to_datetime(self.cleaned_data['start_date'])

    def clean_end_date(self):
        return convert_to_datetime(self.cleaned_data['end_date'])

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['end_date'] <= cleaned_data['start_date']:
            raise forms.ValidationError('Start Date Must be Before End Date')
        if cleaned_data['end_date'] - cleaned_data['start_date'] >= datetime.timedelta(days=45):
            raise forms.ValidationError('Time Span Must be Less Than 45 Days')
        if cleaned_data['end_date'] > datetime.datetime.now(tz=pytz.timezone('US/Eastern')):
            raise forms.ValidationError('Do Not Choose a Day Later Than the Current Day')
        return cleaned_data


class ManualSearch(forms.Form):
    user_input = forms.CharField(widget=forms.TextInput(attrs=
                                                        {'class': 'res-tt-model-search-box', 'placeholder':
                                                            '4501 H2...'})
                                 , max_length=100, min_length=2, help_text='Enter error name, model number, or both')

    def clean_user_input(self):
        user_request = self.cleaned_data['user_input'].split(' ')
        bad_input = ''
        queried_items = {
            'errors': [],
            'models': []
        }

        for item in user_request:
            found_errors = len(queried_items['errors'])
            found_models = len(queried_items['models'])
            if len(item) < 2:
                bad_input += ' \"' + item + '\"'
                continue
            if Error.objects.filter(error_name__icontains=item):
                queried_items['errors'].append(item)
            if ProductModel.objects.filter(model_number__icontains=item):
                queried_items['models'].append(item)
            if not len(queried_items['errors']) > found_errors and not len(queried_items['models']) > found_models:
                bad_input += ' \"' + item + '\"'

        if len(bad_input):
            raise forms.ValidationError('The following input is bad; Please fix: ' + bad_input)

        return queried_items


class CustomFixForm(forms.ModelForm):
    steps_to_fix_error = SummernoteTextFormField(label='Enter detailed steps on how to resolve issue:')

    class Meta:
        model = CustomFixes
        fields = ['symptoms', 'steps_to_fix_error', 'repairs_error', 'model_id']
        widgets = {
            'repairs_error': forms.SelectMultiple(attrs={'class': 'select-multiple'}),
            'model_id': forms.SelectMultiple(attrs={'class': 'select-multiple'}),
        }


class ErrorForm(forms.ModelForm):

    class Meta:
        model = Error
        fields = ['error_name', 'error_title', 'error_description']
        widgets = {
            'error_description': forms.Textarea(attrs={'cols': '85'}),
        }
