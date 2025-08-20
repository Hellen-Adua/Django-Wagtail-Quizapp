import csv
from django.core.management.base import BaseCommand
from quiz.models import Category, Quiz, Question, Choice

class Command(BaseCommand):
    help = "Import questions from CSV with nested categories"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **kwargs):
        path = kwargs["csv_file"]
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Build / find nested category path
                parent = None
                for part in [p.strip() for p in row["category"].split("/") if p.strip()]:
                    parent, _ = Category.objects.get_or_create(name=part, parent=parent)

                # Create or get quiz (you can adapt this if CSV has a quiz title column)
                quiz_title = row.get("quiz_title") or parent.name
                quiz, _ = Quiz.objects.get_or_create(title=quiz_title, category=parent)

                # Create question
                q = Question.objects.create(
                    quiz=quiz,
                    text=row["question"],
                    correct_explanation=row.get("explanation_correct", "").strip() or None
                )

                # Choices A–D
                correct_letter = row["correct_choice"].strip().upper()
                for letter in ["A","B","C","D"]:
                    text = row[f"choice_{letter.lower()}"].strip()
                    exp_key = f"explanation_{'correct' if letter==correct_letter else 'wrong'}"
                    Choice.objects.create(
                        question=q,
                        text=text,
                        is_correct=(letter == correct_letter),
                        explanation=(row.get(exp_key) or "").strip() or None
                    )

        self.stdout.write(self.style.SUCCESS("Import complete"))
