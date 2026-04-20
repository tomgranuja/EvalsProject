import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from .models import Teacher, Student, Subject, SubjectStudent, EvalDesign
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import SubjectStudentEnrollFormSet, SubjectStudentEditFormSet, EvalDesignForm

# Bypass authentication decorators
# Comment out in order to use them

# def login_required(func=None, redirect_field_name='next', login_url=None):
#     def decorator(f):
#         def wrapper(*args, **kwargs):
#             return f(*args, **kwargs)
#         return wrapper
#     if func is None:
#         return decorator
#     else:
#         return decorator(func)

# def user_passes_test(test_func, login_url=None, redirect_field_name='next'):
#     def decorator(f):
#         def wrapper(*args, **kwargs):
#             return f(*args, **kwargs)
#         return wrapper
#     return decorator

# Create your views here.

def index(request):
    return HttpResponseRedirect(reverse(teachers))

def is_teacher(user):
    return Teacher.active.filter(user=user.pk).exists()

def is_teacher_or_staff(user):
    return is_teacher(user) or user.is_staff

@login_required
def profile(request):
    if is_teacher(request.user):
        return HttpResponseRedirect(reverse(teacher_dashboard, args=[request.user.pk]))
    else:
        return HttpResponseRedirect(reverse(teachers))


def teachers(request):
    teachers = Teacher.active.all()
    return render(request, 
                  'evaluations/teachers.html',
                  {'teachers': teachers,})

@user_passes_test(is_teacher_or_staff)
@login_required
def teacher_dashboard(request, teacher_pk):
    evals_by_subject = _teacher_evals_by_subject(teacher_pk)
    evals_count = sum(
        [len(evaluations) for evaluations in evals_by_subject.values()]
        )
    context = {
        'subjects' : Subject.objects.filter(teacher = teacher_pk),
        'teacher' : Teacher.objects.get(pk=teacher_pk),
        'evaluations': evals_by_subject,
        'evaluations_count': evals_count,
        }
    return render(request, 'evaluations/teacher_dashboard.html', context)
    
def _teacher_evals_by_subject(teacher_pk):
    teacher_evals = {}
    for subject in Subject.objects.filter(teacher = teacher_pk):
        teacher_evals[subject] = subject.evaldesign_set.all()
    return teacher_evals

def subjects(request):
    subjects = Subject.objects.all()
    return render(request, 
                  'evaluations/subjects.html',
                  {'subjects': subjects,})

@user_passes_test(is_teacher_or_staff)
@login_required
def subject_student_enroll(request, subject_pk):
    subject = Subject.objects.get(pk=subject_pk)
    students = Student.active.exclude(cycle__name='Retirado').order_by('cycle')
    initial = _student_enroll_form_initial(subject_pk)
    
    if request.method == 'POST':
        formset = SubjectStudentEnrollFormSet(request.POST, initial=initial)
        if formset.is_valid():
            _student_enroll_formset_to_db(formset, subject_pk)
            return HttpResponseRedirect(reverse(subject_student_edit, args=[subject_pk]))
    else:
        formset = SubjectStudentEnrollFormSet(initial=initial)
    return render(request,
                  'evaluations/subject_student_enroll.html',
                  {'formset': formset,
                   'subject': subject,
                   })

def _student_enroll_form_initial(subject_pk):
    return [ {'student': s,
              'enroll_field': s.has_subject_student(subject_pk),
                  }
             for s in Student.active.exclude(cycle__name='Retirado').order_by('cycle','grade')]

def _student_enroll_formset_to_db(formset, subject_pk):
    done = {'added': [], 'removed':[]}
    for form in formset:
        if form.has_changed():
            student = form.initial['student']
            if form.cleaned_data['enroll_field']:
                student.subject_set.add(subject_pk)
                done['added'].append(student.pk)
            else:
                student.subject_set.remove(subject_pk)
                done['removed'].append(student.pk)
    return done
                  
@user_passes_test(is_teacher_or_staff)
@login_required
def subject_student_edit(request, subject_pk):
    subject = Subject.objects.get(pk=subject_pk)
    # evaluations = subject.evaldesign_set.all()
    initial = _student_edit_form_initial(subject_pk)

    if request.method == 'POST':
        formset = SubjectStudentEditFormSet(request.POST, initial=initial)
        hlines = ['<h2>Recived a POST request</h2>']
        if formset.is_valid():
            pks = _student_edit_formset_to_db(formset, subject_pk)
            students = Student.objects.filter(subjectstudent__pk__in=pks)
            hlines.append(f'<p> Change made to {[str(s) for s in students]} </p>')
        else:
            hlines.append('<h2>Data does not validate</h2>')
            hline.append(f'{form.errors}')
        hlines.append(
            (f'<p><a href="{reverse(subject_student_edit, args=[subject_pk])}">'
            f'Back to Subject edit</a></p>'
            ))
        return HttpResponse('\n'.join(hlines))
    else:
        formset = SubjectStudentEditFormSet(initial=initial)
    
    return render(request,
                  'evaluations/subject_student_edit.html',
                  {'formset': formset,
                   'subject': subject,})
                   # 'evaluations': evaluations,})

def _student_edit_form_initial(subject_pk):
    return [
        {
            'subject_student': s,
            'active_field': s.active,
            'informed_field': s.informed,
            }
        for s in SubjectStudent.user_active.filter(subject=subject_pk).order_by('student__cycle', 'student__grade')
        ]

def _student_edit_formset_to_db(formset, subject_pk):
    changed = []
    for form in formset:
        if form.has_changed():
            subject_student = form.initial['subject_student']
            subject_student.active = form.cleaned_data['active_field']
            subject_student.informed = form.cleaned_data['informed_field']
            subject_student.save()
            changed.append(subject_student.pk)
    return changed

@user_passes_test(is_teacher_or_staff)
@login_required
def eval_design_new(request, subject_pk):
    initial = {
        'subject': Subject.objects.get(pk=subject_pk),
        'subject_students': SubjectStudent.user_active.filter(subject=subject_pk, active=True),
        }
    eval_design = EvalDesign(subject=initial['subject'])
    if request.method == 'POST':
        form = EvalDesignForm(request.POST, initial=initial, instance=eval_design)
        if form.is_valid():
            eval_design = form.save()
            url_anchor = _back_to_subject_on_dashboard_anchor(eval_design)
            return HttpResponseRedirect(url_anchor)
    else:
        form = EvalDesignForm(initial=initial, instance=eval_design)
    return render(request,
                  'evaluations/eval_design.html',
                  {'form': form})

@user_passes_test(is_teacher_or_staff)
@login_required
def eval_design_edit(request, subject_pk, eval_design_pk):
    initial = {
        'subject': Subject.objects.get(pk=subject_pk),
        }
    eval_design = EvalDesign.objects.get(pk=eval_design_pk)
    if request.method == 'POST':
        form = EvalDesignForm(request.POST, initial=initial, instance=eval_design)
        if form.is_valid():
            eval_design = form.save()
            url_anchor = _back_to_subject_on_dashboard_anchor(eval_design)
            return HttpResponseRedirect(url_anchor)
    else:
        form = EvalDesignForm(initial=initial, instance=eval_design)
    return render(request,
                  'evaluations/eval_design.html',
                  {'form': form,})

def _back_to_subject_on_dashboard_anchor(eval_design):
    'Teacher dashboard url with subject id html anchor.'

    subject = eval_design.subject
    teacher = subject.teacher
    url = reverse(teacher_dashboard, args=[teacher.pk])
    return f'{url}#subject-{subject.pk}-evals'

@user_passes_test(is_teacher_or_staff)
@login_required
def eval_results(request, subject_pk, eval_design_pk):
    eval_design = EvalDesign.objects.get(pk=eval_design_pk)
    table_headers = ['Id', 'Estudiante', 'Nota', 'Comentario']
    initial_table = []
    for r in eval_design.evalresult_set.exclude(subject_student__student__user__is_active=False):
        initial_table.append( [
            r.pk,
            str(r.subject_student.student),
            r.score,
            r.comment,
            ] )
    
    if request.method == 'POST':
        body_data = request.body.decode('utf-8')
        body_dic = json.loads(body_data)
        for i,(pk, fname, r, c) in enumerate(body_dic['data']):
            if (body_dic['initial'][i][2] != r or
                body_dic['initial'][i][3] != c ):
                evalresult = eval_design.evalresult_set.get(pk=pk)
                evalresult.score = r
                evalresult.comment = c
                evalresult.save()
        return JsonResponse({
            'message': 'Data saved',
            'data': [
                [
                    r.pk,
                    str(r.subject_student.student),
                    r.score,
                    r.comment,
                    ]
                for r in eval_design.evalresult_set.exclude(subject_student__student__user__is_active=False)
                ]
            },
            safe=False,
            )
    
    return render(request,
                  'evaluations/eval_results.html',
                  {'eval_design': eval_design,
                   'table_info': {
                       'table_headers': table_headers,
                       'data': initial_table,
                       'fetch_url': reverse(eval_results, args=[subject_pk, eval_design_pk]),
                       },
                   })

@user_passes_test(is_teacher_or_staff)
@login_required
def subject_eval_results(request, subject_pk):
    subject = Subject.objects.get(pk=subject_pk)
    eval_designs = EvalDesign.objects.filter(subject=subject)
    students = subject.students.exclude(user__is_active=False)
    # TODO
    # Student not included in certain evaldesign
    # should have their handsontable cell disabled
    initial_table = _subject_eval_results_table(
        eval_designs,students
        )
    table_headers = ['id', 'Estudiante']
    column_settings = [
        {'data': 'pk','type': 'numeric', 'readOnly': True},
        {'data': 'name', 'readOnly': True},
        ]
    for e in eval_designs:
        table_headers.append(e.name[:10])
        column_settings.append({'data': str(e.pk), 'type': 'numeric'})
    
    if request.method == 'POST':
        body_data = request.body.decode('utf-8')
        body_dic = json.loads(body_data)
        
        # print(body_dic)
        # Hope there is a better way
        # to do this
        # ...
        for initial_dic, current in zip(body_dic['initial'], body_dic['data']):
            current_dic = {
                key: current[i]
                for i,key in enumerate(
                    [settings['data'] for settings in column_settings]
                    )
                }
            for key in initial_dic:
                if key in ['pk','name']:
                    continue
                score_needs_update = (
                    (initial_dic[key] != current_dic[key]) &
                    isinstance(current_dic[key], int | None)
                    )
                if score_needs_update:
                    eval_design = eval_designs.get(pk=int(key))
                    eval_result = eval_design.evalresult_set.get(
                        subject_student__student__pk=initial_dic['pk']
                        )
                    eval_result.score = current_dic[key]
                    eval_result.save()
        return JsonResponse(
            {
                'message': 'Data saved',
                'data': _subject_eval_results_table(
                    eval_designs,students
                    )
            },
            safe=False,
            )

    return render(request,
                  'evaluations/subject_eval_results.html',
                  {'subject': subject,
                   'table_info': {
                       'table_headers': table_headers,
                       'column_settings': column_settings,
                       'data': initial_table,
                       'fetch_url': reverse(subject_eval_results, args=[subject.pk]),
                       },
                   })
                  
def _subject_eval_results_table(eval_designs, students):
    table = []
    for st in students:
        row = {'pk': st.pk, 'name': str(st) }
        for eval_design in eval_designs:
            if eval_design.evalresult_set.filter(subject_student__student=st).exists():
                r = eval_design.evalresult_set.get(subject_student__student=st)
                row[str(eval_design.pk)] = r.score
        table.append(row)
    return table

def thanks(request):
    return render(request, 'evaluations/thanks.html')

def test_none_var(request):
    return render(request,
                  'evaluations/test_none.html',
                  {'none_obj': {'none_var': None}})

def hamburguer(request):
    return render(request, 'evaluations/hamburguer.html')
