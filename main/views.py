from django.shortcuts import render, redirect, get_object_or_404
from .models import Citation
from .forms import CitationForm
import random

from django.http import JsonResponse


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

    context = {
        'citation': citation,
        'user_liked': request.session.get(f'liked_{citation.id}'),
        'user_disliked': request.session.get(f'disliked_{citation.id}'),
    }
    return render(request, 'citations/show_random_citation.html', context)


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


def vote(request, citation_id):
    citation = get_object_or_404(Citation, id=citation_id)
    action = request.GET.get('action')

    # Для хранения результатов голосования -> используем ключи
    like_key = f'liked_{citation_id}'
    dislike_key = f'disliked_{citation_id}'

    if action == 'like':
        # Отмена лайка
        if request.session.get(like_key):
            citation.likes -= 1
            del request.session[like_key]
        else:
            # Новый лайк
            citation.likes += 1
            request.session[like_key] = True
            # Отмена дизлайка
            if request.session.get(dislike_key):
                citation.dislikes -= 1
                del request.session[dislike_key]

    elif action == 'dislike':
        if request.session.get(dislike_key):
            citation.dislikes -= 1
            del request.session[dislike_key]
        else:
            citation.dislikes += 1
            request.session[dislike_key] = True
            if request.session.get(like_key):
                citation.likes -= 1
                del request.session[like_key]

    citation.save()
    return JsonResponse({'likes': citation.likes,
                         'dislikes': citation.dislikes,
                         'user_action':
                             'like' if request.session.get(like_key)
                             else 'dislike' if request.session.get(dislike_key)
                             else None})
