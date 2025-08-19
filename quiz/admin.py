from django.contrib import admin
from .models import Category, Quiz, Question, Choice
# Register your models here.

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ("text", "quiz")

admin.site.register(Category)
admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)