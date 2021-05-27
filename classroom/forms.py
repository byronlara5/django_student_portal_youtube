from django import forms
from ckeditor.widgets import CKEditorWidget

from classroom.models import Course, Category


class NewCourseForm(forms.ModelForm):
	picture = forms.ImageField(required=True)
	title = forms.CharField(widget=forms.TextInput(attrs={'class': 'validate'}), required=True)
	description = forms.CharField(widget=forms.TextInput(attrs={'class': 'validate'}), required=True)
	category = forms.ModelChoiceField(queryset=Category.objects.all())
	syllabus = forms.CharField(widget=CKEditorWidget())

	class Meta:
		model = Course
		fields = ('picture', 'title', 'description', 'category', 'syllabus')
