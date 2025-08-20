from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey("Quiz", on_delete=models.CASCADE)
    score = models.IntegerField()
    answers = models.JSONField(default=dict)  # {question_id: choice_id}
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.taken_at})"


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="children")
    
    class Meta:
        unique_together = ("name", "parent")

    def __str__(self):
        return self.name

    def full_path(self):
        return f"{self.parent.full_path()}/{self.name}" if self.parent else self.name

class Quiz(models.Model):
    title = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="quizzes")
    def __str__(self): 
        return f"{self.title} ({self.category.full_path()})"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()
        # Optional general explanation for the correct answer (fallback)
    correct_explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.text[:80]
    
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
        # Explanation shown when THIS option is selected (wrong) OR when it’s the correct one
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.text} ({'✓' if self.is_correct else '✗'})"

class UserQuizResult(models.Model):
    user = models.ForeignKey(User, related_name="quiz_results", on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name="results", on_delete=models.CASCADE)
    score = models.IntegerField()
    total = models.IntegerField()
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} • {self.quiz.title} • {self.score}/{self.total}"


class UserAnswer(models.Model):
    result = models.ForeignKey(UserQuizResult, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    is_correct = models.BooleanField()

    class Meta:
        unique_together = ("result", "question")