from django.db import models
# from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from evaluations.models import Student, Subject

# Create your models here.

class GradeScheme(models.Model):
    '''Grading scheme that could be qualitative.'''

    name = models.CharField(max_length=60)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class GradeOption(models.Model):
    '''One grade option for a grading scheme.'''

    grade_scheme = models.ForeignKey(GradeScheme, related_name='grade_options', on_delete=models.CASCADE)
    quality = models.CharField(max_length=40, blank=True)
    rank = models.SmallIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['grade_scheme', 'rank'],
                name='unique_grade_scheme_rank_combination',
                violation_error_message='This rank already exists in the grading scheme.',
            ),
        ]

    def __str__(self):
        s = str(self.rank)
        if self.quality != '':
            s += f': {self.quality}'
        return s

class Rubric(models.Model):
    '''An assessment design with criteria.'''

    name = models.CharField(max_length=60)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class RubricDomain(models.Model):
    '''Domain for grouping rubric criteria.'''

    rubric = models.ForeignKey(Rubric, related_name='domains', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    rank = models.SmallIntegerField()
    weight = models.PositiveSmallIntegerField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['rubric', 'rank'],
                name='unique_rubric_rank_combination_in_domains',
                violation_error_message='This rank already exists in the rubric.',
            ),
        ]

    def __str__(self):
        return self.name

class RubricCriterion(models.Model):
    '''Criterion for a specific rubric.'''

    rubric = models.ForeignKey(Rubric, related_name='criteria', on_delete=models.CASCADE)
    description = models.TextField()
    rank = models.SmallIntegerField()
    weight = models.PositiveSmallIntegerField(blank=True, null=True)
    grade_scheme = models.ForeignKey(GradeScheme, related_name='criteria', on_delete=models.CASCADE)
    rubric_domain = models.ForeignKey(RubricDomain, blank=True, null=True, related_name='criteria', on_delete=models.SET_NULL)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['rubric', 'rank'],
                name='unique_rubric_rank_combination_in_criteria',
                violation_error_message='This rank already exists in the rubric.',
            ),
        ]

    def __str__(self):
        return f'{self.rank}: {self.description}'

class StudentAssessment(models.Model):
    '''A student evaluation in time by a rubric.'''

    student = models.ForeignKey(Student, related_name='assessments', on_delete=models.CASCADE)
    rubric = models.ForeignKey(Rubric, related_name='student_assessments', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, blank=True, null=True, related_name='student_assessments', on_delete=models.SET_NULL)
    start = models.DateTimeField("assessment start", blank=True, null=True)
    end = models.DateTimeField("assessment end", blank=True, null=True)
    note = models.TextField(blank=True)
    feedback = models.TextField(blank=True)

    def __str__(self):
        return f'{self.student} assessment by {self.rubric}'

class CriterionScore(models.Model):
    '''A single criterion score inside a student assessment.'''

    student_assessment = models.ForeignKey(StudentAssessment, related_name='scores', on_delete=models.CASCADE)
    rubric_criterion = models.ForeignKey(RubricCriterion, related_name='student_scores', on_delete=models.CASCADE)
    grade_option = models.ForeignKey(GradeOption, blank=True, null=True, related_name='student_scores', on_delete=models.SET_NULL)
    note = models.TextField(blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['student_assessment', 'rubric_criterion'],
                name='unique_student_assessment_rubric_criterion_combination',
                violation_error_message='This criterion already exists in this assessment.',
            ),
        ]

    def qualify_by_text_or_none(self, text):
        # FUTURE PROOTOTYPING/ERROR MAPPING BLUEPRINT:
        # try:
        #     self.author = Author.objects.get(name__icontains=text_query)
        # except Author.DoesNotExist:
        #     # Handle 404 / API Response Mapping here
        #     raise ObjectDoesNotExist(f"No match for '{text_query}'.")
        # except Author.MultipleObjectsReturned:
        #     # Handle ambiguities here (e.g., return closest match or raise 400)
        #     raise MultipleObjectsReturned(f"Too many matches for '{text_query}'.")

        if text is None or text == '':
            self.grade_option = None
        else:
            try:
                self.grade_option = self.rubric_criterion.grade_scheme.grade_options.get(quality=text)
            except GradeOption.DoesNotExist:
                self.grade_option = None

    def get_quality_or_blank(self):
        quality = ''
        if self.grade_option is not None:
            quality = self.grade_option.quality
        return quality

    def __str__(self):
        return f'{self.grade_option} in {self.student_assessment}'
