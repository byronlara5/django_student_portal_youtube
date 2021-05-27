from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, HttpResponse
from django.core.paginator import Paginator

from question.models import Question, Answer, Votes
from question.forms import QuestionForm, AnswerForm

from classroom.models import Course

def NewStudentQuestion(request, course_id):
	user = request.user
	course = get_object_or_404(Course, id=course_id)

	if request.method == 'POST':
		form = QuestionForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data.get('title')
			body = form.cleaned_data.get('body')
			q = Question.objects.create(user=user, title=title, body=body)
			course.questions.add(q)
			return redirect('modules', course_id=course.id)
	else:
		form = QuestionForm()
	context = {
		'form': form,
	}
	return render(request, 'question/newquestion.html', context)


def Questions(request, course_id):
	course = get_object_or_404(Course, id=course_id)
	questions = course.questions.all()

	#Pagination
	paginator = Paginator(questions, 10)
	page_number = request.GET.get('page')
	questions_data = paginator.get_page(page_number)

	context = {
		'course': course,
		'questions': questions_data,
	}
	return render(request, 'question/questions.html', context)

def QuestionDetail(request, course_id, question_id):
	user = request.user
	moderator = False
	course = get_object_or_404(Course, id=course_id)
	question = get_object_or_404(Question, id=question_id)

	correct_answer = Answer.objects.filter(question=question, is_accepted_answer=True)
	rest_answers = Answer.objects.filter(question=question)

	answers = correct_answer | rest_answers

	if user == course.user or user == question.user:
		moderator = True

	if request.method == 'POST':
		form = AnswerForm(request.POST)
		if form.is_valid():
			body = form.cleaned_data.get('body')
			Answer.objects.create(user=user, question=question, body=body)
			return redirect('question-detail', course_id=course_id, question_id=question_id)
	else:
		form = AnswerForm()
	context = {
		'question': question,
		'answers': answers,
		'course': course,
		'form': form,
		'moderator': moderator,
	}
	return render(request, 'question/question.html', context)

def MarkAsAnswer(request, course_id, question_id, answer_id):
	user = request.user
	course = get_object_or_404(Course, id=course_id)
	question = get_object_or_404(Question, id=question_id)

	if user == course.user or user == question.user:
		answer = get_object_or_404(Answer, id=answer_id)
		answer.is_accepted_answer = True
		answer.save()
		question.has_accepted_answer = True
		question.save()
		return redirect('question-detail', course_id=course_id, question_id=question_id)
	else:
		return HttpResponseForbidden()
		
def VoteAnswer(request, course_id, question_id):
	user = request.user
	answer_id = request.POST['answer_id']
	vote_type = request.POST['vote_type']
	try:
		answer = get_object_or_404(Answer, id=answer_id)
		voted = Votes.objects.filter(user=user, answer=answer)
		if voted:
			voted.delete()
		else:
			if vote_type == 'U':
				Votes.objects.create(user=user, answer=answer, vote='U')
			else:
				Votes.objects.create(user=user, answer=answer, vote='D')
		return HttpResponse(answer.calculate_votes())
	except Exception as e:
		raise e