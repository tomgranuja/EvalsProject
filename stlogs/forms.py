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

