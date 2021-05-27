from django.contrib import admin
from quiz.models import Answer, Question, Quizzes, Attempter, Attempt

# Register your models here.
admin.site.register(Answer)
admin.site.register(Question)
admin.site.register(Quizzes)
admin.site.register(Attempt)
admin.site.register(Attempter)
