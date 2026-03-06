from django.contrib import admin

# Register your models here.
from .models import Cycle, Teacher, Student, Subject, SubjectStudent, EvalDesign, EvalResult

admin.site.register(Cycle)
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(SubjectStudent)

#@admin.register(Subject)
#class SubjectAdmin(admin.ModelAdmin):
#    filter_horizontal = ('students',)

# admin.site.register(Student)
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('model_str', 'cycle', 'model_grade_display')

    @admin.display(description='Name', ordering='pk')
    def model_str(self, o):
        return str(o)

    @admin.display(description='Grade', ordering='grade')
    def model_grade_display(self, o):
        return o.grade_display()

# admin.site.register(EvalDesign)
@admin.register(EvalDesign)
class EvalDesignAdmin(admin.ModelAdmin):
   list_display = ('name', 'subject', 'subject__teacher', 'informed')

# admin.site.register(EvalResult)
@admin.register(EvalResult)
class EvalResultAdmin(admin.ModelAdmin):
    list_display = ('subject_student', 'eval_design', 'eval_design__subject', 'eval_design__subject__teacher')
