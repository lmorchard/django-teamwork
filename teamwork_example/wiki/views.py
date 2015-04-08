from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

from teamwork.shortcuts import get_object_or_404_or_403

from teamwork_example.wiki.models import Document
from teamwork_example.wiki.forms import DocumentCreateForm, DocumentEditForm


def view(request, name):
    document = get_object_or_404_or_403('view_document', request.user,
                                        Document, name=name)

    perms = request.user.get_all_permissions(document)

    return render(request, 'wiki/view.html', dict(
        document=document, perms=perms
    ))


def create(request):
    """Create a new wiki document"""
    base_perms = request.user.get_all_permissions()
    if 'wiki.add_document' not in base_perms:
        raise PermissionDenied()

    parent_pk = request.GET.get('parent', None)
    if not parent_pk:
        parent = None
    else:
        parent = get_object_or_404_or_403(
            'add_document_child', request.user, Document, pk=parent_pk)

    if 'POST' != request.method:
        form = DocumentCreateForm()
    else:
        form = DocumentCreateForm(request.POST)
        if form.is_valid():
            document = form.save(commit=False)
            if parent:
                document.parent = parent
            document.creator = request.user
            document.save()
            return redirect(document.get_absolute_url())

    return render(request, 'wiki/create.html', dict(
        parent=parent, form=form
    ))


def edit(request, name):
    document = get_object_or_404_or_403('change_document', request.user,
                                        Document, name=name)

    if 'POST' != request.method:
        form = DocumentEditForm(instance=document)
    else:
        form = DocumentEditForm(request.POST, instance=document)
        if form.is_valid():
            document = form.save()
            return redirect(document.get_absolute_url())

    return render(request, 'wiki/edit.html', dict(
        document=document, form=form
    ))


def delete(request, name):
    document = get_object_or_404_or_403('delete_document', request.user,
                                        Document, name=name)

    if 'POST' == request.method:
        document.delete()
        return redirect(reverse('base.views.index'))

    return render(request, 'wiki/delete.html', dict(
        document=document
    ))
