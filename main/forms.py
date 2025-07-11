from django import forms
from django.core.exceptions import ValidationError
from .models import Citation


class CitationForm(forms.ModelForm):
    class Meta:
        model = Citation
        fields = ['text', 'source']

    def clean_text(self):
        text = self.cleaned_data.get('text')

        # Кастомизация сообщения, если более 2000 символов
        if len(text) > 2000:
            raise ValidationError("Цитата слишком длинная (максимум 2000 символов)!")

        # Проверка на уникальность цитаты
        if text and Citation.objects.filter(text=text).exists():
            raise ValidationError("Цитата уже существует, попробуйте другую!")

        return text

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get('source')

        # Проверка на количество цитат из одного источника
        if source:
            citation_count = Citation.objects.filter(source=source).count()
            if citation_count >= 3:
                self.add_error('source', "У одного источника не может быть более трех цитат!")

        return cleaned_data


