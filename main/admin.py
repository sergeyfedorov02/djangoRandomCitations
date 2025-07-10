from django.contrib import admin
from .models import Citation


# Register your models here.
@admin.register(Citation)
class CitationAdmin(admin.ModelAdmin):
    list_display = ['text', 'source', 'weight', 'likes', 'dislikes', 'views']
    search_fields = ['text', 'source']  # по каким параметрам можно будет искать
    list_filter = ['weight', 'likes', 'dislikes', 'views']  # по каким параметрам можно будет фильтровать
    list_editable = ['weight']  # параметры, которые можно будет изменять

