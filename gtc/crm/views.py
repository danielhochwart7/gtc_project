from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.serializers import serialize
from django.shortcuts import render, redirect, get_object_or_404
from .models import Contact
from .forms import ContactForm
import json


# def create(req):
#     form = ContactForm(req.POST or None, req.FILES or None)
#
#     if form.is_valid():
#         form.save()
#         return redirect('read_all')
#
#     return render(req, 'contact_form.html', {'form': form})


@login_required
def contacts_all(req):

    if req.method == 'GET':
        contacts = serialize('json', Contact.objects.all())

        parsed_contacts = json.loads(contacts)

        list_contacts = list()
        for item in parsed_contacts:
            pk = item['pk']
            contact = item['fields']
            contact.update({'id': pk})
            list_contacts.append(contact)

        payload = {
            'contacts': list_contacts
        }

        return JsonResponse(payload, content_type='application/json', status=200)
    else:
        return JsonResponse("Method not allowed", content_type='text/plain', status=405)


@login_required
@require_http_methods(['GET', 'DELETE', 'PATCH'])
def contact(req, contact_id):

    print('req.method', req.method)
    if req.method == 'GET':
        contact = get_object_or_404(Contact, pk=contact_id)
        payload = {
            'contacts':
            {
                'id': contact.pk,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
            }
        }

    elif req.method == 'DELETE':
        contact = get_object_or_404(Contact, pk=contact_id)
        payload = {
            'contacts': [
                {
                    'id': contact.pk,
                    'first_name': contact.first_name,
                    'last_name': contact.last_name,
                }
            ]
        }
        contact.delete()
        return JsonResponse(payload, content_type='application/json', status=200)

    elif req.method == 'PATCH':
        contact = Contact.objects.get(pk=contact_id)
        new_values= json.loads(req.body.decode('utf8'))['contacts']
        print(new_values)
        contact = get_object_or_404(Contact, pk=contact_id)
        contact.first_name = new_values['first_name']
        contact.last_name = new_values['last_name']
        contact.save()

        payload = {
            'contacts':
            {
                'id': contact.pk,
                'first_name': contact.first_name,
                'last_name': contact.last_name,
            }
        }

    return JsonResponse(payload, content_type='application/json', status=200)

# def update(req, id):
#     contact = get_object_or_404(Contact, pk=id)
#     form = ContactForm(req.POST or None, req.FILES or None, instance=contact)
#
#     if form.is_valid():
#         form.save()
#         return redirect('read_all')
#
#     return render(req, 'contact_form.html', {'form': form})
#
#
# def delete(req, id):
#     contact = get_object_or_404(Contact, pk=id)
#
#     if req.method == 'DELETE':
#         contact.delete()
#         return redirect('read_all')
#     else:
#         print('Errrroou')
#
#     return render(req, 'contact_delete_confirm.html', {'contact': contact})