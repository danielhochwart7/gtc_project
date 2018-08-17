from django.shortcuts import render, redirect, get_object_or_404
from .models import Contact
from .forms import ContactForm


def create(req):
    form = ContactForm(req.POST or None, req.FILES or None)

    if form.is_valid():
        form.save()
        return redirect('read_all')

    return render(req, 'contact_form.html', {'form': form})


def read_all(req):
    contacts = Contact.objects.all()
    return render(req, 'contact.html', {'contacts': contacts})


def update(req, id):
    contact = get_object_or_404(Contact, pk=id)
    form = ContactForm(req.POST or None, req.FILES or None, instance=contact)

    if form.is_valid():
        form.save()
        return redirect('read_all')

    return render(req, 'contact_form.html', {'form': form})


def delete(req, id):
    contact = get_object_or_404(Contact, pk=id)

    if req.method == 'POST':
        contact.delete()
        return redirect('read_all')

    return render(req, 'contact_delete_confirm.html', {'contact': contact})