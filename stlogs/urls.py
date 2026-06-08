from django.urls import path

from . import views

urlpatterns = [
    path('students/',
         views.students,
         name="stlogs_students"),
    path('students/<int:student_pk>/assessments/',
         views.student_assessments,
         name="student_assessments"),
    path('students/<int:student_pk>/assessments/new_assessment/',
         views.new_student_assessment,
         name="new_student_assessment"),
    path('assessments/',
         views.assessments,
         name="stlogs_assessments"),
    path('assessments/<int:assessment_pk>/',
         views.edit_assessment,
         name="edit_assessment"),
    path('assessments/<int:assessment_pk>/scores',
         views.student_assessment_scores,
         name="student_assessment_scores"),
]
