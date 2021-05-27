from django.db import models
from django.contrib.auth.models import User

from classroom.models import Course
from page.models import Page
from quiz.models import Quizzes
from assignment.models import Assignment

# Create your models here.

class Completion(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	course = models.ForeignKey(Course, on_delete=models.CASCADE)
	completed = models.DateTimeField(auto_now_add=True)
	page = models.ForeignKey(Page, on_delete=models.CASCADE, blank=True, null=True)
	quiz = models.ForeignKey(Quizzes, on_delete=models.CASCADE, blank=True, null=True)
	assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, blank=True, null=True)

	def __str__(self):
		return self.user.username