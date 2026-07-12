import datetime
from django.utils import timezone
from django import forms
from .models import StudentAssessment

class StudentAssessmentForm(forms.ModelForm):

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
        widgets = {
            'start': forms.DateInput(attrs={'type': 'date'}),
            'end': forms.DateInput(attrs={'type': 'date'}),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'student' in self.fields:
            self.fields['student'].disabled = True

    def clean_start(self):
        user_date = self.cleaned_data.get('start')
        if not user_date:
            return None
        if isinstance(user_date, datetime.datetime):
            user_date = user_date.date()
        if self.instance and self.instance.pk and self.instance.start:
            local_existing_date = timezone.localdate(self.instance.start)
            target_time = timezone.localtime(self.instance.start).time()
        else:
            target_time = datetime.time(12,0)
        local_naive = datetime.datetime.combine(
            user_date,
            target_time,
            )
        return timezone.make_aware(local_naive)

    def clean_end(self):
        user_date = self.cleaned_data.get('end')
        if not user_date:
            return None
        if isinstance(user_date, datetime.datetime):
            user_date = user_date.date()
        if self.instance and self.instance.pk and self.instance.end:
            local_existing_date = timezone.localdate(self.instance.end)
            target_time = timezone.localtime(self.instance.end).time()
        else:
            target_time = datetime.time(12,0)
        local_naive = datetime.datetime.combine(
            user_date,
            target_time,
            )
        return timezone.make_aware(local_naive)

