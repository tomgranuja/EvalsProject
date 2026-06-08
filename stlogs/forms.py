from django import forms
from .models import StudentAssessment

CUSTOM_DATE_INPUT_ATTRS = {'type': 'date', 'class': 'form-control'}
CUSTOM_TIME_INPUT_ATTRS = {'type': 'time', 'class': 'form-control'}

class StudentAssessmentForm(forms.ModelForm):

    start = forms.SplitDateTimeField(
        required=False,
        label="Comienzo",
        widget=forms.SplitDateTimeWidget(
            date_attrs=CUSTOM_DATE_INPUT_ATTRS,
            time_attrs=CUSTOM_TIME_INPUT_ATTRS,
        )
    )

    end = forms.SplitDateTimeField(
        required=False,
        label="Fin",
        widget=forms.SplitDateTimeWidget(
            date_attrs=CUSTOM_DATE_INPUT_ATTRS,
            time_attrs=CUSTOM_TIME_INPUT_ATTRS,
        )
    )

    class Meta:
        model = StudentAssessment
        fields = [ 'student', 'rubric', 'start', 'end', 'subject', 'note', 'feedback' ]
        labels = {
            'student': 'Estudiante',
            'rubric': 'Pauta',
            'start': 'Comienzo',
            'end': 'Fin',
            'subject': 'Asignatura (Opcional)',
            'note': 'Nota/Recordatorio',
            'feedback': 'Comentario a la familia',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'student' in self.fields:
            self.fields['student'].disabled = True

