from django.urls import path

from . import views

urlpatterns = [
    path('',
         views.today_attendance,
         name='today_attendance',
         ),
    path('activities/',
         views.activities,
         name='activities',
         ),
    path('activities/none_found/',
         views.activity_none_found,
         name='activity_none_found',
         ),
    path('activities/<int:activity_pk>/attendance/nomina/',
         views.activity_attendance_nomina,
         name='activity_attendance_nomina',
         ),
    path('activities/<int:activity_pk>/attendance/cycles/',
         views.activity_attendance_cycles,
         name='activity_attendance_cycles',
         ),
    path('activities/<int:activity_pk>/attendance/cycles/all/',
         views.activity_attendance_all_cycles,
         name='activity_attendance_all_cycles',
         ),
    path('activities/<int:activity_pk>/attendance/cycles/<int:cycle_pk>/',
         views.activity_attendance_single_cycle,
         name='activity_attendance_single_cycle',
         ),
    # path('months/',
    #      views.months,
    #      name='months'
    #      ),
    # path('months/<int:month>/days/',
    #      views.days,
    #      name='days'
    #      ),
    # path('months/<int:month>/days/<int:day>/',
    #      views.day_activities,
    #      name='day_activities'
    #      ),
    ]
