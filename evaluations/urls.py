from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.index,
         name='index'
         ),
    path('profile',
         views.profile,
         name='profile'),
    path('teachers',
         views.teachers,
         name='teachers'
         ),
    path('teachers/<int:teacher_pk>/dashboard',
         views.teacher_dashboard,
         name='teacher_dashboard'
         ),
    path('subjects',
         views.subjects,
         name='subjects'
         ),
    path('subjects/<int:subject_pk>/subject_student_enroll',
         views.subject_student_enroll,
         name='subject_student_enroll'
         ),
    path('subjects/<int:subject_pk>/subject_student_edit',
         views.subject_student_edit,
         name='subject_student_edit'
         ),
    path('subjects/<int:subject_pk>/eval_results',
         views.subject_eval_results,
         name='subject_eval_results'
         ),
    path('subjects/<int:subject_pk>/eval_designs/new_eval_design',
         views.eval_design_new,
         name='eval_design_new'
         ),
    path('subjects/<int:subject_pk>/eval_designs/<int:eval_design_pk>',
         views.eval_design_edit,
         name='eval_design_edit'
         ),
    path('subjects/<int:subject_pk>/eval_designs/<int:eval_design_pk>/eval_results',
         views.eval_results,
         name='eval_results'
         ),
    path('thanks',
         views.thanks,
         name="thanks"),
    path('test_none',
         views.test_none_var,
         name="test_none"),
    path('hamburguer',
         views.hamburguer,
         name="hamburguer"),
    ]
