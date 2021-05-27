from django.contrib import admin
from question.models import Votes, Answer, Question

# Register your models here.
admin.site.register(Votes)
admin.site.register(Answer)
admin.site.register(Question)