from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

from evaluations.models import Student

# Create your models here.
def _null_or_blank(obj):
    return (obj is None) or (obj is '')

class SchoolActivity(models.Model):
    '''An attendance registrable school activity.'''

    ActivityType = models.IntegerChoices('ActivityType', 'Común Salida Encuentro Paseo')

    start = models.DateTimeField('Start')
    end = models.DateTimeField('End', blank=True, null=True)
    activity_type = models.PositiveSmallIntegerField(
        choices=ActivityType,
        default=ActivityType.Común
        )
    students = models.ManyToManyField(
        Student,
        through="Attendance"
        )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(end__date=F('start__date')) | Q(end__date=None),
                name='activity_start_and_end_on_same_date'
                )
            ]

    def __str__(self):
        return self.start.strftime('%b-%d ') + self.get_activity_type_display()

class Attendance(models.Model):
    'SchoolActivity-Student attendance through table'
    activity = models.ForeignKey(SchoolActivity, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)
    late_time = models.TimeField(blank=True, null=True)
    retire_time = models.TimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["activity", "student"],
                name="unique_activity_student"
            )
        ]

    # For form level validation
    def clean(self):
        super().clean()
        # Ensure that if is not presente, don't have late or retire time.
        if not self.present:
            if not _null_or_blank(self.late_time):
                raise ValidationError('Cannot be a late time if it is not present.')
            if not _null_or_blank(self.retire_time):
                raise ValidationError('Cannot be a retire time if it is not present.')

    # For database level integrity
    def save(self, *args, **kwargs):
        # Ensure that if is not presente, don't have late or retire time.
        if not self.present:
            self.late_time = None
            self.retire_time = None
        super().save(*args, **kwargs)

    def is_present_long_display(self):
        if self.present:
            return 'presente'
        else:
            return 'ausente'

    def __str__(self):
        return f'{self.student.user.first_name} at {self.activity}'

