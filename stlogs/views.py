import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from evaluations.models import Student, CustomReport
from .models import StudentAssessment, CriterionScore
from .forms import StudentAssessmentForm
from utils.view_helpers import is_teacher_or_staff

# Create your views here.

def students(request):
    students = Student.active.all().order_by(
        'cycle',
        'grade',
    )
    return render(
        request,
        'stlogs/students.html',
        {
            'students': students,
        },
    )

@user_passes_test(is_teacher_or_staff)
@login_required
def student_assessments(request, student_pk):
    student = Student.objects.get(pk=student_pk)
    assessments = StudentAssessment.objects.filter(student=student).order_by('end')
    custom_reports = CustomReport.objects.all()
    return render(
        request,
        'stlogs/student_assessments.html',
        {
            'student': student,
            'assessments': assessments,
            'custom_reports': custom_reports,
        },
    )

@user_passes_test(is_teacher_or_staff)
@login_required
def new_student_assessment(request, student_pk):
    student = Student.objects.get(pk=student_pk)
    if request.method == 'POST':
        form = StudentAssessmentForm(request.POST, initial={'student': student})
        if form.is_valid():
            student_assessment = form.save()
            # Create non-qualified yet criteria scores
            for criterion in student_assessment.rubric.criteria.order_by('rank'):
                score = CriterionScore(
                    student_assessment=student_assessment,
                    rubric_criterion=criterion,
                )
                score.save()
            return render(
                request,
                'stlogs/student_assessment_success.html',
                {'student_assessment': student_assessment},
            )
    else:
        form = StudentAssessmentForm(initial={'student': student})

    return render(
            request,
            'stlogs/student_assessment.html',
            {
                'form': form,
            },
    )

def assessments(request):
    assessments = StudentAssessment.objects.filter(
        student__in=Student.active.values('pk')
    ).select_related('student__cycle', 'rubric')
    return render(
        request,
        'stlogs/assessments.html',
        {
            'assessments': assessments,
        }
    )

@user_passes_test(is_teacher_or_staff)
@login_required
def edit_assessment(request, assessment_pk):
    assessment = StudentAssessment.objects.get(pk=assessment_pk)
    if request.method == 'POST':
        form = StudentAssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            student_assessment = form.save()
            return render(
                request,
                'stlogs/student_assessment_success.html',
                {'student_assessment': student_assessment},
            )
    else:
        form = StudentAssessmentForm(instance=assessment)

    return render(
            request,
            'stlogs/student_assessment.html',
            {
                'form': form,
            },
    )

@user_passes_test(is_teacher_or_staff)
@login_required
def student_assessment_scores(request, assessment_pk):

    assessment = StudentAssessment.objects.get(pk=assessment_pk)
    scores = assessment.scores.order_by('rubric_criterion__rank')
    table_headers = ['Id', 'N', 'Criterio', 'Opción', 'Nota/Recordatorio', 'Comentario a la familia']
    column_settings = [
        {'type': 'numeric', 'readOnly': True},
          {'type': 'numeric', 'readOnly': True},
          {'type': 'text', 'readOnly': True},
          {'type': 'text',},
          {'type': 'text'},
          {'type': 'text'},
    ]
    cell_settings = [
        {
            'row': i,
            'col': 3,
            'type': 'dropdown',
            'stric': True,
            'allowInvalid': True,
            'source': [
                option.quality
                for option in score.rubric_criterion.grade_scheme.grade_options.order_by('-rank')
                ] + ['']
        }
        for i,score in enumerate(scores)
        ]
    initial_table = [
        [
            score.pk,
            score.rubric_criterion.rank,
            score.rubric_criterion.description,
            score.get_quality_or_blank(),
            score.note,
            score.feedback,
        ]
        for score in scores
    ]
    if request.method == 'POST':
        body_data = request.body.decode('utf-8')
        body_dic = json.loads(body_data)
        for i,(pk, rank, criterion, quality, note, feedback) in enumerate(body_dic['data']):
            score = None
            if body_dic['initial'][i][3] != quality:
                if score is None:
                    score = CriterionScore.objects.get(pk=pk)
                score.qualify_by_text_or_none(quality)
            if body_dic['initial'][i][4] != note:
                if score is None:
                    score = CriterionScore.objects.get(pk=pk)
                if note is None:
                    note = ''
                score.note = note
            if body_dic['initial'][i][5] != feedback:
                if score is None:
                    score = CriterionScore.objects.get(pk=pk)
                if feedback is None:
                    feedback = ''
                score.feedback = feedback
            if score is not None:
                score.save()
        return JsonResponse({
            'message': 'Data saved',
            'data': [
                [
                    score.pk,
                    score.rubric_criterion.rank,
                    score.rubric_criterion.description,
                    score.get_quality_or_blank(),
                    score.note,
                    score.feedback,
                    ]
                for score in assessment.scores.order_by('rubric_criterion__rank')
                ]
            },
            safe=False,
            )

    return render(
        request,
        'stlogs/student_assessment_scores.html',
        {
            'assessment': assessment,
            'table_info': {
                       'table_headers': table_headers,
                       'column_settings': column_settings,
                       'cell_settings': cell_settings,
                       'data': initial_table,
                       'fetch_url': reverse(student_assessment_scores, args=[assessment_pk]),
                       },
        },
    )

