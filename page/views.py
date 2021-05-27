from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from page.models import Page, PostFileContent
from classroom.models import Course
from module.models import Module
from completion.models import Completion

from page.forms import NewPageForm

# Create your views here.

@login_required
def NewPageModule(request, course_id, module_id):
	user = request.user
	course = get_object_or_404(Course, id=course_id)
	module = get_object_or_404(Module, id=module_id)
	files_objs = []

	if user != course.user:
		return HttpResponseForbidden()

	else:
		if request.method == 'POST':
			form = NewPageForm(request.POST, request.FILES)
			if form.is_valid():
				title = form.cleaned_data.get('title')
				content = form.cleaned_data.get('content')
				files = request.FILES.getlist('files')

				for file in files:
					file_instance = PostFileContent(file=file, user=user)
					file_instance.save()
					files_objs.append(file_instance)

				p = Page.objects.create(title=title, content=content, user=user)
				p.files.set(files_objs)
				p.save()
				module.pages.add(p)
				return redirect('modules', course_id=course_id)
		else:
			form = NewPageForm()
	context = {
		'form': form,
	}

	return render(request, 'page/newpage.html', context)


def PageDetail(request, course_id, module_id, page_id):
	page = get_object_or_404(Page, id=page_id)
	completed = Completion.objects.filter(course_id=course_id, user=request.user, page_id=page_id).exists()

	context = {
		'page': page,
		'completed': completed,
		'course_id': course_id,
		'module_id': module_id,
	}
	return render(request, 'page/page.html', context)


def MarkPageAsDone(request, course_id, module_id, page_id):
	user = request.user
	page = get_object_or_404(Page, id=page_id)
	course = get_object_or_404(Course, id=course_id) 
	Completion.objects.create(user=user, course=course, page=page)
	return redirect('modules', course_id=course_id)

