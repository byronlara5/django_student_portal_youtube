from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from quiz.forms import NewQuizForm, NewQuestionForm
from quiz.models import Answer, Question, Quizzes, Attempter, Attempt
from module.models import Module
from completion.models import Completion

# Create your views here.

def NewQuiz(request, course_id, module_id):
	user = request.user
	module = get_object_or_404(Module, id=module_id)
	if request.method == 'POST':
		form = NewQuizForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data.get('title')
			description = form.cleaned_data.get('description')
			due = form.cleaned_data.get('due')
			allowed_attempts = form.cleaned_data.get('allowed_attempts')
			time_limit_mins = form.cleaned_data.get('time_limit_mins')
			quiz = Quizzes.objects.create(user=user, title=title, description=description, due=due, allowed_attempts=allowed_attempts, time_limit_mins=time_limit_mins)
			module.quizzes.add(quiz)
			module.save()
			return redirect('new-question', course_id=course_id, module_id=module_id, quiz_id=quiz.id)
	else:
		form = NewQuizForm()

	context = {
		'form': form,
	}
	return render(request, 'quiz/newquiz.html', context)


def NewQuestion(request, course_id, module_id, quiz_id):
	user = request.user
	quiz = get_object_or_404(Quizzes, id=quiz_id)
	if request.method == 'POST':
		form = NewQuestionForm(request.POST)
		if form.is_valid():
			question_text = form.cleaned_data.get('question_text')
			points = form.cleaned_data.get('points')
			answer_text = request.POST.getlist('answer_text')
			is_correct = request.POST.getlist('is_correct')

			question = Question.objects.create(question_text=question_text, user=user, points=points)

			for a, c in zip(answer_text, is_correct):
				answer = Answer.objects.create(answer_text=a, is_correct=c, user=user)
				question.answers.add(answer)
				question.save()
				quiz.questions.add(question)
				quiz.save()
			return redirect('new-question', course_id=course_id, module_id=module_id, quiz_id=quiz.id)
	else:
		form = NewQuestionForm()

	context = {
		'form': form,
	}
	return render(request, 'quiz/newquestion.html', context)


def QuizDetail(request, course_id, module_id, quiz_id):
	user = request.user
	quiz = get_object_or_404(Quizzes, id=quiz_id)
	my_attempts = Attempter.objects.filter(quiz=quiz, user=user)

	context = {
		'quiz': quiz,
		'my_attempts': my_attempts,
		'course_id': course_id,
		'module_id': module_id,
	}
	return render(request, 'quiz/quizdetail.html', context)

def TakeQuiz(request, course_id, module_id, quiz_id):
	quiz = get_object_or_404(Quizzes, id=quiz_id)
	context = {
		'quiz': quiz,
		'course_id': course_id,
		'module_id': module_id,
	}
	return render(request, 'quiz/takequiz.html', context)


def SubmitAttempt(request, course_id, module_id, quiz_id):
	user = request.user
	quiz = get_object_or_404(Quizzes, id=quiz_id)
	earned_points = 0
	if request.method == 'POST':
		questions = request.POST.getlist('question')
		answers = request.POST.getlist('answer')
		attempter = Attempter.objects.create(user=user, quiz=quiz, score=0)

		for q, a in zip(questions, answers):
			question = Question.objects.get(id=q)
			answer = Answer.objects.get(id=a)
			Attempt.objects.create(quiz=quiz, attempter=attempter, question=question, answer=answer)
			Completion.objects.create(user=user, course_id=course_id, quiz=quiz)
			if answer.is_correct == True:
				earned_points += question.points
				attempter.score += earned_points
				attempter.save()
		return redirect('index')


def AttemptDetail(request, course_id, module_id, quiz_id, attempt_id):
	user = request.user
	quiz = get_object_or_404(Quizzes, id=quiz_id)
	attempts = Attempt.objects.filter(quiz=quiz, attempter__user=user)

	context = {
		'quiz': quiz,
		'attempts': attempts,
		'course_id': course_id,
		'module_id': module_id,
	}
	return render(request, 'quiz/attemptdetail.html', context)
