from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.views.decorators.http import require_http_methods
from .models import Quiz, Question, Choice, UserQuizResult, UserAnswer, UserAttempt
from django.http import Http404
from django.db import transaction
from .forms import AnswerForm

def quiz_list(request):
    quizzes = Quiz.objects.select_related("category").all()
    return render(request, "quiz/quiz_list.html", {"quizzes": quizzes})


@login_required
def take_quiz(request, quiz_id):
    # Fetch the quiz with its questions, choices, and category
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related("questions__choices", "category"),
        pk=quiz_id
    )

    quiz_questions = list(quiz.questions.all())

    # Handle case where quiz has no questions
    if not quiz_questions:
        return render(request, "quiz/empty_quiz.html", {"quiz": quiz})

    if request.method == "POST":
        # Track selected answers and score
        user_selected_answers = {}  # question_id -> chosen_choice
        correct_answer_count = 0

        for question in quiz_questions:
            submitted_choice_id = request.POST.get(f"q_{question.id}")
            if not submitted_choice_id:
                continue

            try:
                chosen_choice = question.choices.get(pk=submitted_choice_id)
            except Choice.DoesNotExist:
                continue

            user_selected_answers[question.id] = chosen_choice

            if chosen_choice.is_correct:
                correct_answer_count += 1

        # Save results and user answers in one transaction
        with transaction.atomic():
            quiz_result = UserQuizResult.objects.create(
                user=request.user,
                quiz=quiz,
                score=correct_answer_count,
                total=len(quiz_questions),
            )

            for question in quiz_questions:
                chosen_choice = user_selected_answers.get(question.id)
                if chosen_choice:
                    UserAnswer.objects.create(
                        result=quiz_result,
                        question=question,
                        choice=chosen_choice,
                        is_correct=chosen_choice.is_correct,
                    )

        return redirect("quiz_result", result_id=quiz_result.id)

    # If GET request → render quiz form
    return render(
        request,
        "quiz/take_quiz.html",
        {"quiz": quiz, "questions": quiz_questions}
    )


@login_required
def quiz_result(request, result_id):
    # Fetch the user's quiz result, with related quiz, category, questions, and choices
    user_quiz_result = get_object_or_404(
        UserQuizResult.objects
        .select_related("quiz__category")
        .prefetch_related("answers__question__choices", "answers__choice"),
        pk=result_id
    )

    # Ensure only the quiz owner or staff can view the result
    if user_quiz_result.user != request.user and not request.user.is_staff:
        raise Http404()

    # Build a data structure for rendering in the template
    # Each block represents one question with choices, user’s answer, and correct answer
    question_blocks = []
    for user_answer in user_quiz_result.answers.all():
        question = user_answer.question
        all_choices = list(question.choices.all())
        selected_choice = user_answer.choice
        correct_choice = next((choice for choice in all_choices if choice.is_correct), None)

        question_blocks.append({
            "question": question,
            "choices": all_choices,
            "selected_choice": selected_choice,
            "correct_choice": correct_choice,
        })

    return render(
        request,
        "quiz/result.html",
        {
            "result": user_quiz_result,
            "quiz": user_quiz_result.quiz,
            "question_blocks": question_blocks,
        }
    )


@login_required
def my_results(request):
    # Fetch all results for the logged-in user, most recent first
    user_results = (
        UserQuizResult.objects
        .filter(user=request.user)
        .select_related("quiz")
        .order_by("-taken_at")
    )

    return render(
        request,
        "quiz/my_results.html",
        {"results": user_results}
    )


@login_required
def quiz_revision(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    # Retrieve past attempt (assuming you save user answers in a model)
    user_attempt = UserAttempt.objects.filter(user=request.user, quiz=quiz).last()

    context = {
        "quiz": quiz,
        "questions": quiz.question_set.all(),
        "user_answers": user_attempt.answers if user_attempt else {},
    }
    return render(request, "quiz_revision.html", context)


@login_required
def submit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    if request.method == "POST":
        answers = {}
        score = 0

        for question in quiz.question_set.all():
            choice_id = request.POST.get(f"question_{question.id}")
            if choice_id:
                answers[question.id] = int(choice_id)
                choice = Choice.objects.get(pk=choice_id)
                if choice.is_correct:
                    score += 1

        # Save attempt
        attempt = UserAttempt.objects.create(
            user=request.user,
            quiz=quiz,
            score=score,
            answers=answers
        )

        return redirect("quiz_result", result_id=attempt.id)

    # If accessed directly
    return redirect("quiz_detail", quiz_id=quiz.id)