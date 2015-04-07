from django.shortcuts import render
from django.contrib.auth import get_user_model
from teamwork_example.wiki.models import Document
from teamwork.models import Team


def index(request):
    users = get_user_model().objects.all()
    documents = Document.objects.filter(parent=None).all()
    teams = Team.objects.all()
    return render(request, 'base/index.html', dict(
        users=users, documents=documents, teams=teams
    ))
