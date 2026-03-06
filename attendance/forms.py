from django.forms import ModelForm, Form, BooleanField, TimeInput, formset_factory
from .models import Attendance

class AttendanceForm(ModelForm):
    class Meta:
        model = Attendance
        fields = ['present', 'late_time', 'retire_time']
        widgets = {
            'late_time': TimeInput(attrs={'type': 'time'}),
            'retire_time': TimeInput(attrs={'type': 'time'}),
            }

class AttendanceNominaForm(Form):
    include = BooleanField(required=False)

AttendanceFormSet = formset_factory(AttendanceForm, extra=0, max_num=100)
AttendanceNominaFormSet = formset_factory(AttendanceNominaForm, extra=0, max_num=100)
