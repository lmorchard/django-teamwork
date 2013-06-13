from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Permission
from teamwork_example.wiki.models import Document
from teamwork.models import Team, Role

def view(request, name):
    document = get_object_or_404(Document, name=name)
    return render(request, 'wiki/view.html', dict(
        document=document
    ))
