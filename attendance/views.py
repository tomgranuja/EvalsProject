import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from evaluations.models import Cycle, Teacher
from evaluations.views import is_teacher_or_staff
from .models import SchoolActivity, Attendance, Student
from .forms import AttendanceFormSet, AttendanceNominaFormSet

# Create your views here.

def today_attendance(request):
    activities = SchoolActivity.objects.filter(start__date=datetime.date.today())
    if activities.exists():
        return HttpResponseRedirect(reverse(
            activity_attendance_cycles,
            args=[activities.first().pk]
            ))
    else:
        return HttpResponseRedirect(reverse(activity_none_found))

def activity_none_found(request):
    return render(
        request,
        'attendance/activity_none_found.html',
        )

def activities(request):
    return render(
        request,
        'attendance/activities.html',
        {
            'activities': SchoolActivity.objects.all(),
            },
        )

def activity_attendance_cycles(request, activity_pk):
    return render(
        request,
        'attendance/activity_attendance_cycles.html',
        {
            'activity': SchoolActivity.objects.get(pk=activity_pk),
            'cycles': Cycle.objects.all(),
            },
        )

@user_passes_test(is_teacher_or_staff)
@login_required
def activity_attendance_nomina(request, activity_pk, cycle_pk=None):
    activity = SchoolActivity.objects.get(pk=activity_pk)
    cycles = Cycle.objects.all()
    if cycle_pk is not None:
        cycles = cycles.filter(pk=cycle_pk)
    students = Student.objects.filter(cycle__in=cycles)
    initial = [{
        'student': st,
        'include': activity.students.filter(pk=st.pk).exists()
        } for st in Student.objects.filter(cycle__in=cycles).order_by('cycle', 'grade')]
    if request.method == 'POST':
        formset = AttendanceNominaFormSet(request.POST, initial=initial)
        if formset.is_valid():
            for form in formset:
                if form.has_changed():
                    if form.cleaned_data['include']:
                        activity.students.add(form.initial['student'])
                    else:
                        activity.students.remove(form.initial['student'])
            return HttpResponseRedirect(reverse(activity_attendance_all_cycles, args=[activity_pk]))
    else:
        formset = AttendanceNominaFormSet(initial=initial)
    return render(
        request,
        'attendance/activity_attendance_nomina.html',
        {
            'activity': activity,
            'cycles': cycles,
            'formset': formset,
            },
        )

@user_passes_test(is_teacher_or_staff)
@login_required
def activity_attendance_all_cycles(request, activity_pk):
    cycles = Cycle.objects.all()
    activity = SchoolActivity.objects.get(pk=activity_pk)
    initial = _attendance_formset_initial(activity, cycles)
    # print(f'###Initial data for formset:\n{initial}\n')
    if request.method == 'POST':
        formset = AttendanceFormSet(request.POST, initial=initial)
        if formset.is_valid():
            pks = _attendance_formset_to_db(formset)
            attendances = Attendance.objects.filter(pk__in=pks).order_by('student__cycle')
            return render(
                request,
                'attendance/activity_attendance_success.html',
                {
                    'activity': activity,
                    'cycles': cycles,
                    'attendances': attendances,
                    },
                )
    else:
        formset = AttendanceFormSet(initial=initial)

    return render(
        request,
        'attendance/activity_attendance_register.html',
        {
            'activity': activity,
            'cycles': cycles,
            'formset': formset,
            },
        )

@user_passes_test(is_teacher_or_staff)
@login_required
def activity_attendance_single_cycle(request, activity_pk, cycle_pk):
    activity = SchoolActivity.objects.get(pk=activity_pk)
    cycle = Cycle.objects.get(pk=cycle_pk)
    initial = _attendance_formset_initial(activity, cycle)
    # print(initial)
    if request.method == 'POST':
        #print(f'#####Se recibió el siguiente POST: \n{request.POST}\n#######Fin del POST')
        formset = AttendanceFormSet(request.POST, initial=initial)
        if formset.is_valid():
            pks = _attendance_formset_to_db(formset)
            attendances = Attendance.objects.filter(pk__in=pks).order_by('student__cycle')
            return render(
                request,
                'attendance/activity_attendance_success.html',
                {
                    'activity': activity,
                    'cycles': [cycle],
                    'attendances': attendances,
                    },
                )
    else:
        formset = AttendanceFormSet(initial=initial)

    return render(
        request,
        'attendance/activity_attendance_register.html',
        {
            'activity': activity,
            'cycles': [cycle],
            'formset': formset,
            },
        )

def _attendance_formset_to_db(formset):
    registered = []
    for form in formset:
        attendance, created = Attendance.objects.get_or_create(
            activity    = form.initial['activity'],
            student     = form.initial['student'],
            )
        attendance.present = form.cleaned_data['present']
        attendance.late_time   = form.cleaned_data['late_time']
        attendance.retire_time = form.cleaned_data['retire_time']
        attendance.save()
        registered.append(attendance.pk)
    return registered

def _attendance_formset_initial(activity, cycles):
    if isinstance(cycles, Cycle):
        cycles = [cycles]
    initial = []
    students = activity.students.filter(cycle__in=cycles)
    if students.exists():
        for student in students:
            attendance = Attendance.objects.get(activity=activity, student=student)
            initial.append({
                'activity': activity,
                'student': student,
                'present': attendance.present,
                'late_time': attendance.late_time,
                'retire_time': attendance.retire_time,
                })
    else:
        students = Student.objects.filter(cycle__in=cycles)
        for student in students:
            initial.append({
                'activity': activity,
                'student': student,
                'present': False,
                'late_time': None,
                'retire_time': None,
                })
    return initial
