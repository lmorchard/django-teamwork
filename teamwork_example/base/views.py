from django.shortcuts import render
from django.contrib.auth.models import User, Permission
from teamwork_example.wiki.models import Document
from teamwork.models import Team, Role

def index(request):
    users = User.objects.all()
    documents = Document.objects.all()
    teams = Team.objects.all()
    return render(request, 'base/index.html', dict(
        users=users, documents=documents, teams=teams
    ))
