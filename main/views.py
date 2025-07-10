from django.shortcuts import render, redirect
from .models import Citation
from .forms import CitationForm
import random


# Create your views here.
def show_random_citation(request):
    citations = Citation.objects.all()

    # Если нет ни одной цитаты в БД -> оповестим об этом пользователя
    if not citations.exists():
        return render(request, 'citations/show_random_citation.html', {'message': "Извините, никаких цитат нет!"})

    # Если есть -> выберем и отобразим случайную на основе веса (и увеличим счетчик показа)
    citation = random.choices(citations, weights=[c.weight for c in citations])[0]
    citation.views += 1
    citation.save()

    return render(request, 'citations/show_random_citation.html', {'citation': citation})


def add_citation(request):
    if request.method == "POST":
        form = CitationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('show_random_citation')

    # Пользователь только открыл страницу для добавления цитаты (получит пустую форму)
    else:
        form = CitationForm()

    # Генерации html страницы
    return render(request, 'citations/add_citation.html', {'form': form})


def show_top_citations(request):
    # Получим список из 10 цитат, отсортированных по убыванию лайков
    citations = Citation.objects.all().order_by('-likes')[:10]
    return render(request, 'citations/show_top_citations.html', {'citations': citations})
