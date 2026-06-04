from django.contrib import admin

# Register your models here.
from .models import GradeScheme, GradeOption, Rubric, RubricDomain, RubricCriterion, StudentAssessment, CriterionScore

admin.site.register(GradeScheme)
admin.site.register(GradeOption)
admin.site.register(Rubric)
admin.site.register(RubricDomain)
admin.site.register(RubricCriterion)
admin.site.register(StudentAssessment)
admin.site.register(CriterionScore)
