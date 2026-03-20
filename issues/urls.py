from django.urls import path
from issues.views import handle_reporters, handle_issues, index

urlpatterns = [
    path('', index, name='index'),                              # type: ignore
    path('reporters/', handle_reporters, name='reporters'),     # type: ignore
    path('issues/', handle_issues, name='issues'),              # type: ignore
]