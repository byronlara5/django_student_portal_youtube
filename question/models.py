from django.db import models
from django.contrib.auth.models import User

#3rd apps field
from ckeditor.fields import RichTextField

# Create your models here.

VOTES_CHOICES = (
	('U', 'Up Vote'),
	('D', 'Down Vote'),
)

class Question(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_user')
	title = models.CharField(max_length=300)
	body = RichTextField()
	created_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField(auto_now_add=True)
	has_accepted_answer = models.BooleanField(default=False)

	def __str__(self):
		return self.title

	def get_answers_count(self):
		return Answer.objects.filter(question=self).count()


class Answer(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answer_user')
	question = models.ForeignKey(Question, on_delete=models.CASCADE)
	body = RichTextField()
	created_date = models.DateTimeField(auto_now_add=True)
	update_date = models.DateTimeField(auto_now_add=True)
	votes = models.IntegerField(default=0)
	is_accepted_answer = models.BooleanField(default=False)

	def __str__(self):
		return self.user.username

	def calculate_votes(self):
		u_votes = Votes.objects.filter(answer=self, vote='U').count()
		d_votes = Votes.objects.filter(answer=self, vote='D').count()
		self.votes = u_votes - d_votes
		self.save()
		return self.votes

class Votes(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes_user')
	answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='answer_votes')
	vote = models.CharField(choices=VOTES_CHOICES, max_length=1)
	date = models.DateTimeField(auto_now_add=True)
