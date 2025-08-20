from django.urls import path
from . import views

urlpatterns = [
    path("", views.quiz_list, name="quiz_list"),
    path("<int:quiz_id>/", views.take_quiz, name="take_quiz"),
    path("result/<int:result_id>/", views.quiz_result, name="quiz_result"),
    path("my/results/", views.my_results, name="my_results"),
]