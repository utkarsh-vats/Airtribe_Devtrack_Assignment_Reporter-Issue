from django.urls import path
from issues.views import handle_reporters, handle_issues

urlpatterns = [
    path('reporters/', handle_reporters, name='reporters'),     # type: ignore
    path('issues/', handle_issues, name='issues'),              # type: ignore
]