from evaluations.models import Teacher
from attendance.models import Attendance

def is_teacher(user):
    return Teacher.active.filter(user=user.pk).exists()

def is_teacher_or_staff(user):
    return is_teacher(user) or user.is_staff

def student_attendance_resume(st):
    attendance = Attendance.objects.filter(student=st)
    present = attendance.filter(present=True)
    attendance_count = attendance.count()
    present_count = present.count()
    rate =  present_count / attendance_count
    return {
        'present': present_count,
        'attendance': attendance_count,
        'percent': f'{rate*100:.0f}',
        }

def student_assessment_table(assessment):
    looped_domains_ranks = []
    table = []
    for criterion_score in assessment.scores.order_by('rubric_criterion__rank'):
        criterion = criterion_score.rubric_criterion
        domain = criterion.rubric_domain
        if domain is not None:
            if domain.rank not in looped_domains_ranks:
                table.append({
                    'type': 'domain',
                    'data': [ domain.rank, domain.name ],
                })
            looped_domains_ranks.append(domain.rank)
        table.append({
            'type': 'criteria',
            'data': [
                criterion.rank,
                criterion.description,
                criterion_score.get_quality_or_blank(),
            ],
        })
    return table
