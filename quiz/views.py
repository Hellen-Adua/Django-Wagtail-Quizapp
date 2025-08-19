from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from django.views.decorators.http import require_http_methods
from .models import Quiz, Question, Choice
from .forms import AnswerForm

def quiz_list(request):
    return render(request, "quiz/quiz_list.html", {"quizzes": Quiz.objects.all()})

@require_http_methods(["GET", "POST"])
def take_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    question = quiz.questions.first()
    result = None

    if not question:
        return render(request, "quiz/empty_quiz.html", {"quiz": quiz})

    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            choice = get_object_or_404(Choice, pk=form.cleaned_data["choice_id"], question=question)
            result = "Correct ✅" if choice.is_correct else "Wrong ❌"
    else:
        form = AnswerForm()

    return render(request, "quiz/take_quiz.html", {"quiz": quiz, "question": question, "form": form, "result": result})