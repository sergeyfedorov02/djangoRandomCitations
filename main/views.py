from django.shortcuts import render, redirect, get_object_or_404
from .models import Citation
from .forms import CitationForm
import random

from django.http import JsonResponse

from django.db import transaction
from django.db.models import F


# Create your views here.
def show_random_citation(request):
    citations = Citation.objects.all()

    # Если нет ни одной цитаты в БД -> оповестим об этом пользователя
    if not citations.exists():
        return render(request, 'citations/show_random_citation.html', {'message': "Извините, никаких цитат нет!"})

    # Если есть -> выберем и отобразим случайную на основе веса (и увеличим счетчик показа)
    citation = random.choices(citations, weights=[c.weight for c in citations])[0]
    citation.process_view()
    citation.refresh_from_db()

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
    with transaction.atomic():
        # select_for_update блокирует запись для конкурентных запросов
        citation = Citation.objects.select_for_update().get(pk=citation_id)
        action = request.GET.get('action')
        like_key = f'liked_{citation_id}'
        dislike_key = f'disliked_{citation_id}'

        was_liked = like_key in request.session
        was_disliked = dislike_key in request.session

        # Если ставим лайк ->
        if action == 'like':
            # Если уже был -> отменяем
            if was_liked:
                Citation.objects.filter(pk=citation_id).update(likes=F('likes') - 1)
                del request.session[like_key]
            else:
                # Если НЕ был -> ставим + отменяем дизлайк (если был)
                updates = {'likes': F('likes') + 1}
                if was_disliked:
                    updates['dislikes'] = F('dislikes') - 1
                    del request.session[dislike_key]
                Citation.objects.filter(pk=citation_id).update(**updates)
                request.session[like_key] = True

        # Если ставим дизлайк ->
        elif action == 'dislike':
            # Если уже был -> отменяем
            if was_disliked:
                Citation.objects.filter(pk=citation_id).update(dislikes=F('dislikes') - 1)
                del request.session[dislike_key]
            else:
                # Если НЕ был -> ставим + отменяем лайк (если был)
                updates = {'dislikes': F('dislikes') + 1}
                if was_liked:
                    updates['likes'] = F('likes') - 1
                    del request.session[like_key]
                Citation.objects.filter(pk=citation_id).update(**updates)
                request.session[dislike_key] = True

        request.session.modified = True
        citation.refresh_from_db()

        return JsonResponse({
            'likes': citation.likes,
            'dislikes': citation.dislikes,
            'user_action': action if not (was_liked if action == 'like' else was_disliked) else None
        })
