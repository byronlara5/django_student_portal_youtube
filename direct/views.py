from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseBadRequest, JsonResponse, HttpResponseForbidden

from django.contrib.auth.models import User
from direct.models import Message

from classroom.models import Course

from django.contrib.humanize.templatetags.humanize import naturaltime
# Create your views here.

@login_required
def Broadcast(request):
    user = request.user
    courses = Course.objects.filter(user=user)

    course_select = request.GET.get('course_select')
    body = request.GET.get('message')

    if course_select and body:
        course = Course.objects.get(id=course_select)

        if user != course.user:
            return HttpResponseForbidden()
        else:
            for student in course.enrolled.all():
                Message.send_message(user, student, body)
            return redirect('inbox')

    context = {
        'courses': courses
    }

    return render(request, 'direct/broadcast.html', context)


@login_required
def PeopleWeCanMessage(request):
    user = request.user
    courses = Course.objects.filter(Q(enrolled=user) | Q(user=user))
    course_select = request.GET.get('course_select')
    students = None

    if course_select:
        students = Course.objects.get(id=course_select)

    context = {
        'courses': courses,
        'students': students,
    }
    
    return render(request, 'direct/can_message_list.html', context)

@login_required
def NewConversation(request, username):
    from_user = request.user
    to_user = get_object_or_404(User, username=username)
    body = 'Started a new conversation'

    if from_user != to_user:
        try:
            Message.objects.create(user=from_user, sender=from_user, body=body, recipient=to_user)
        except Exception as e:
            raise e
        return redirect('inbox')

@login_required
def inbox(request):
    messages = Message.get_messages(user=request.user)

    #Pagination
    paginator_messages = Paginator(messages, 5)
    page_number_messages = request.GET.get('messagespage')
    messages_data = paginator_messages.get_page(page_number_messages)

    context = {
        'messages': messages_data,
    }

    return render(request, 'direct/inbox.html', context)

@login_required
def Directs(request, username):
    user = request.user
    messages = Message.get_messages(user=request.user)
    active_direct = username
    directs = Message.objects.filter(user=user, recipient__username=username).order_by('-date')
    directs.update(is_read=True)

    for message in messages:
        if message['user'].username==username:
            message['unread'] = 0
    
    #Pagination for directs
    paginator_directs = Paginator(directs, 5)
    page_number_directs = request.GET.get('directspage')
    directs_data = paginator_directs.get_page(page_number_directs)
    
    context = {
        'directs': directs_data,
        'messages': messages,
        'active_direct': active_direct
    }

    return render(request, 'direct/direct.html', context)

@login_required
def SendDirect(request):
    from_user = request.user
    to_user_username = request.POST.get('to_user')
    body = request.POST.get('body')

    if request.method == 'POST':
        to_user = get_object_or_404(User, username=to_user_username)
        Message.send_message(from_user, to_user, body)
        return HttpResponseRedirect(reverse('directs', args=[to_user_username]))
    else:
        HttpResponseBadRequest()

def LoadMore(request):
    user = request.user

    if request.is_ajax():
        username = request.POST.get('username')
        page_number_directs = request.POST.get('directspage')

        directs = Message.objects.filter(user=user, recipient__username=username).order_by('-date').values(
            'sender__profile__picture',
            'sender__first_name',
            'sender__last_name',
            'body',
            'date')

        #Pagination for directs
        paginator_directs = Paginator(directs, 5)

        if paginator_directs.num_pages >= int(page_number_directs):
            directs_data = paginator_directs.get_page(page_number_directs)

            #Creating the list of data
            directs_list = list(directs_data)

            for x in range(len(directs_list)):
                directs_list[x]['date'] = naturaltime(directs_list[x]['date'])
            
            return JsonResponse(directs_list, safe=False)
        else:
            return JsonResponse({'empty': True}, safe=False)

@login_required
def UserSearch(request):
    user = request.user
    query = request.GET.get('q')
    course_select = request.GET.get('course_select')
    
    users_paginator = None
    students_results = []

    courses = Course.objects.filter(enrolled=user)

    if query and course_select:
        students = Course.objects.filter(Q(id=course_select) & Q(enrolled__username__icontains=query)).values_list('enrolled__username', flat=True)

        for student in students:
            st = get_object_or_404(User, username=student)
            students_results.append(st)
        
        #Pagination
        paginator = Paginator(students_results, 6)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

    context = {
        'users': users_paginator,
        'courses': courses
    }

    return render(request, 'direct/search_user.html', context)

def CheckDirects(request):
    directs_count = 0
    if request.user.is_authenticated:
        directs_count = Message.objects.filter(user=request.user, is_read=False).count()
    return {'directs_count': directs_count}