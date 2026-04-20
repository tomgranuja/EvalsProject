from django.db import models
from django.db.models import F
from django.conf import settings
import datetime

# Create your models here.

class Cycle(models.Model):
    '''Multigrade groups with name and description.'''
    
    name = models.CharField(
        max_length=20,
        )
    description = models.TextField(
        blank=True,
        )
    def __str__(self):
        return self.name
    
class UserActiveObjectManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(user__is_active=True)

class Teacher(models.Model):
    '''Extend user for teacher information.'''

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        )
    name = models.CharField(
        max_length=10,
        )
    color = models.CharField(
        max_length=10,
        )
    
    objects = models.Manager()
    active = UserActiveObjectManager()

    def __str__(self):
        return self.name


class Student(models.Model):
    '''Extend user for student information.'''

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True,
        )
    cycle = models.ForeignKey(
        Cycle,
        on_delete=models.CASCADE,
        )
    grade = models.SmallIntegerField('grade', blank=True, null=True)

    def has_subject_student(self, subject_pk):
        return self.subject_set.filter(pk=subject_pk).exists()

    def grade_display(self):
        grade = self.grade
        PRESCHOOL = -1
        PRIMARY   = 1
        SECONDARY = 9
        STOP      = 12
        grade_str = ''
        if self.grade is not None and self.grade <= STOP:
            if grade >= SECONDARY:
                grade_str = 'I II III IV'.split()[grade-SECONDARY] + '°'
            elif grade >= PRIMARY:
                grade_str = str(grade) + '°'
            elif grade >= PRESCHOOL:
                grade_str = 'prekinder kinder'.split()[grade-PRESCHOOL]
        return grade_str

    objects = models.Manager()
    active = UserActiveObjectManager()
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name[0]}.'
    
class Subject(models.Model):
    '''Subject of a single teacher like maths, arts, etc.'''
    
    name = models.CharField(
        max_length=20,
        )
    description = models.TextField(
        blank=True,
        )
    start = models.DateTimeField("subject start", blank=True, null=True)
    end = models.DateTimeField("subject end", blank=True, null=True)
    students = models.ManyToManyField(
        Student,
        through="SubjectStudent"
        )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,)
    informed = models.BooleanField(default=True)
    
    def user_active_students(self):
        return self.students.exclude(user__is_active=False)
    
    def __str__(self):
        return self.name

class UserActiveSubjectStudentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(student__user__is_active=True)

class SubjectStudent(models.Model):
    '''Subject and Student m2m through table.'''
    
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE,
        )
    active = models.BooleanField(default=True)
    informed = models.BooleanField(default=True)
    
    objects = models.Manager()
    user_active = UserActiveSubjectStudentManager()
    
    def __str__(self):
        return f'{self.student} in {self.subject}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "student"],
                name="unique_subject_student"
            )
        ]
    
class EvalDesign(models.Model):
    '''Evaluation design information, subject and weight.'''
    
    name = models.CharField(
        "nombre",
        max_length=30,
        )
    description = models.TextField(
        "descripción",
        blank=True,
        )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE,
        )
    weight = models.PositiveSmallIntegerField(blank=True, null=True)
    max_score = models.PositiveSmallIntegerField(blank=True, null=True)
    start = models.DateTimeField("evaluation start", blank=True, null=True)
    end = models.DateTimeField("evaluation end", blank=True, null=True)
    informed = models.BooleanField(default=True)
    subject_students = models.ManyToManyField(
        SubjectStudent,
        through="EvalResult",
        verbose_name="Estudiantes inscritos"
        )
    
    def user_active_subject_students(self):
        return self.subject_students.exclude(student__user__is_active=False)
    
    def __str__(self):
        return self.name

class EvalResult(models.Model):
    subject_student = models.ForeignKey(
        SubjectStudent, on_delete=models.CASCADE,
        )
    eval_design = models.ForeignKey(
        EvalDesign, on_delete=models.CASCADE,
        )
    score = models.PositiveSmallIntegerField(blank=True, null=True)
    comment = models.TextField(
        blank=True,
        )
    
    def __str__(self):
        return f'{self.subject_student.student} at {self.eval_design}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subject_student", "eval_design"],
                name="unique_subject_student_eval_design"
            )
        ]
