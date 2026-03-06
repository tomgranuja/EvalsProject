from django import forms
from .models import EvalDesign, SubjectStudent

class EvalDesignMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.student} - {obj.student.grade_display()}"

class SubjectStudentEnrollForm(forms.Form):
    enroll_field = forms.BooleanField(required=False)
    
class SubjectStudentEditForm(forms.Form):
    active_field = forms.BooleanField(required=False)
    informed_field = forms.BooleanField(required=False)

SubjectStudentEnrollFormSet = forms.formset_factory(SubjectStudentEnrollForm, extra=0, max_num=100)
SubjectStudentEditFormSet = forms.formset_factory(SubjectStudentEditForm, extra=0, max_num=50)

class EvalDesignForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject_students'] = EvalDesignMultipleChoiceField(
            queryset=SubjectStudent.objects.filter(
                subject=self.initial['subject'],
                active=True,
                ).order_by('student__cycle', 'student__grade')
            )
    class Meta:
        model = EvalDesign
        fields = ['name', 'description', 'subject_students',]
        
        
