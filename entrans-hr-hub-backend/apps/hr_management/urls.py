from django.urls import path
from .api.auth_views import (
    MyTokenObtainPairView, RegisterView, LoginView, GoogleLoginView,
    RefreshTokenView, RequestPasswordResetView, ConfirmPasswordResetView,
    ChangePasswordView
)
from .api.user_views import (
    UserListAPIView, MeView, CreateUserView, UserAdminView,
    UserAdminDetailView, UserAccessLogView, UserRecentActivityView
)
from .api.project_views import (
    ProjectListCreateView, ProjectDetailView, UserProjectListCreateView,
    UserProjectDetailView, ProjectUserRolesView, ProjectUsersView
)
from .api.timesheet_views import (
    TimesheetListCreateView, TimesheetDetailView, UserTimesheetListView,
    ValidateMultipleTimesheetView, PushTimesheetEmailView, TimesheetReminderView
)
from .api.automation_views import (
    PPTAutomationAPI, TimeTrackingAPI, TimeTrackingTemplateAPI,
    TimeTrackingEmailAPI
)
from .api.admin_dashboard_views import (
    AdminDashboardStatsView, AdminRecentActivityView, AdminUpcomingAnniversariesView
)
from .api.leave_views import LeaveRequestListCreateView, LeaveRequestDetailView, LeaveBalanceListView
from .api.attendance_views import AttendanceLogListView, ClockInView, ClockOutView
from .api.notification_views import NotificationListView, NotificationReadView, NotificationDeleteView
from .api.analytics_views import AnalyticsDashboardView
from .api.export_views import ExportAttendanceView, ExportLeaveView
from .api.search_views import GlobalSearchView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
    path("refresh-token/", RefreshTokenView.as_view(), name="refresh-token"),
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("projects/", ProjectListCreateView.as_view(), name="project-list"),
    path("projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path(
        "users/<int:user_id>/projects/",
        ProjectListCreateView.as_view(),
        name="user-projects",
    ),
    path(
        "user-projects/", UserProjectListCreateView.as_view(), name="user-project-list"
    ),
    path(
        "user-projects/<int:pk>/",
        UserProjectDetailView.as_view(),
        name="user-project-detail",
    ),
    path("timesheets/", TimesheetListCreateView.as_view(), name="timesheet-list"),
    path(
        "timesheets/<int:pk>/", TimesheetDetailView.as_view(), name="timesheet-detail"
    ),
    path("ppt-automation/", PPTAutomationAPI.as_view(), name="ppt-automation-api"),
    path(
        "time-tracking/validation/",
        TimeTrackingAPI.as_view(),
        name="time-tracking-validation",
    ),
    path(
        "time-tracking/templates/",
        TimeTrackingTemplateAPI.as_view(),
        name="time-tracking-templates",
    ),
    path(
        "time-tracking/templates/<str:filename>/",
        TimeTrackingTemplateAPI.as_view(),
        name="time-tracking-template-download",
    ),
    path(
        "time-tracking/send-email/",
        TimeTrackingEmailAPI.as_view(),
        name="time-tracking-email",
    ),
    path(
        "request-password-reset/",
        RequestPasswordResetView.as_view(),
        name="request-password-reset",
    ),
    path(
        "confirm-password-reset/",
        ConfirmPasswordResetView.as_view(),
        name="confirm-password-reset",
    ),
    path("user-timesheets/", UserTimesheetListView.as_view(), name="user-timesheets"),
    path(
        "validate-multiple-timesheets/",
        ValidateMultipleTimesheetView.as_view(),
        name="validate-multiple-timesheets",
    ),
    path("push-email/", PushTimesheetEmailView.as_view(), name="push-email"),
    path(
        "project-user-roles/", ProjectUserRolesView.as_view(), name="project-user-roles"
    ),
    path(
        "project-user-roles/<int:project_id>/", ProjectUsersView.as_view(), name="project-users"
    ),
    path("me/", MeView.as_view(), name="me"),
    path("access-logs/", UserAccessLogView.as_view(), name="access-logs"),
    path("user-recent-activities/", UserRecentActivityView.as_view(), name="user-recent-activities"),
    path("create-user/", CreateUserView.as_view(), name="create-user"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("admin-users/", UserAdminView.as_view(), name="admin-users"),
    path("admin-users/<int:user_id>/", UserAdminDetailView.as_view(), name="admin-user-detail"),
    path("send-timesheet-reminders/", TimesheetReminderView.as_view(), name="send-timesheet-reminders"),
    path("admin-dashboard-stats/", AdminDashboardStatsView.as_view(), name="admin-dashboard-stats"),
    path("admin-recent-activity/", AdminRecentActivityView.as_view(), name="admin-recent-activity"),
    path("admin-upcoming-anniversaries/", AdminUpcomingAnniversariesView.as_view(), name="admin-upcoming-anniversaries"),
    
    # New Features Routes
    path("leaves/", LeaveRequestListCreateView.as_view(), name="leave-list-create"),
    path("leaves/<int:pk>/", LeaveRequestDetailView.as_view(), name="leave-detail"),
    path("leaves/balances/", LeaveBalanceListView.as_view(), name="leave-balances"),
    
    path("attendance/", AttendanceLogListView.as_view(), name="attendance-list"),
    path("attendance/clock-in/", ClockInView.as_view(), name="attendance-clock-in"),
    path("attendance/clock-out/", ClockOutView.as_view(), name="attendance-clock-out"),
    
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/read/", NotificationReadView.as_view(), name="notification-read-all"),
    path("notifications/<int:pk>/read/", NotificationReadView.as_view(), name="notification-read-single"),
    path("notifications/<int:pk>/", NotificationDeleteView.as_view(), name="notification-delete"),
    
    path("analytics/dashboard/", AnalyticsDashboardView.as_view(), name="analytics-dashboard"),
    
    path("exports/attendance/", ExportAttendanceView.as_view(), name="export-attendance"),
    path("exports/leaves/", ExportLeaveView.as_view(), name="export-leaves"),
    
    path("search/", GlobalSearchView.as_view(), name="global-search"),
]
