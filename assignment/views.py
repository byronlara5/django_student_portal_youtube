from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from assignment.forms import NewAssignmentForm, NewSubmissionForm
from assignment.models import AssignmentFileContent, Assignment, Submission

from module.models import Module
from classroom.models import Course, Grade
from completion.models import Completion

# Create your views here.
def NewAssignment(request, course_id, module_id):
	user = request.user
	course = get_object_or_404(Course, id=course_id)
	module = get_object_or_404(Module, id=module_id)
	files_objs = []

	if user != course.user:
		return HttpResponseForbidden()
	else:
		if request.method == 'POST':
			form = NewAssignmentForm(request.POST, request.FILES)
			if form.is_valid():
				title = form.cleaned_data.get('title')
				content = form.cleaned_data.get('content')
				points = form.cleaned_data.get('points')
				due = form.cleaned_data.get('due')
				files = request.FILES.getlist('files')

				for file in files:
					file_instance = AssignmentFileContent(file=file, user=user)
					file_instance.save()
					files_objs.append(file_instance)

				a = Assignment.objects.create(title=title, content=content, points=points, due=due, user=user)
				a.files.set(files_objs)
				a.save()
				module.assignments.add(a)
				return redirect('modules', course_id=course_id)
		else:
			form = NewAssignmentForm()
	
	context = {
		'form': form,
	}
	return render(request, 'assignment/newassignment.html', context)


def AssignmentDetail(request, course_id, module_id, assignment_id):
	user = request.user
	assignment = get_object_or_404(Assignment, id=assignment_id)
	my_submissions = Submission.objects.filter(assignment=assignment, user=user)

	context = {
		'assignment': assignment,
		'course_id': course_id,
		'my_submissions': my_submissions,
		'course_id': course_id,
		'module_id': module_id,
	}
	return render(request, 'assignment/assignment.html', context)

def NewSubmission(request, course_id, module_id, assignment_id):
	user = request.user
	assignment = get_object_or_404(Assignment, id=assignment_id)
	course = get_object_or_404(Course, id=course_id)

	if request.method == 'POST':
		form = NewSubmissionForm(request.POST, request.FILES)
		if form.is_valid():
			file = request.FILES.get('file')
			comment = form.cleaned_data.get('comment')
			s = Submission.objects.create(file=file, comment=comment, user=user, assignment=assignment)
			Grade.objects.create(course=course, submission=s)
			Completion.objects.create(user=user, course=course, assignment=assignment)
			return redirect('modules', course_id=course_id)
	else:
		form = NewSubmissionForm()
	context = {
		'form': form,
		'assignment': assignment,
	}
	return render(request, 'assignment/submitassignment.html', context)
