from django.contrib import admin
from classroom.models import Course, Category

# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
	prepopulated_fields = {"slug": ("title",)}

admin.site.register(Course)
admin.site.register(Category, CategoryAdmin)