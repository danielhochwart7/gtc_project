from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from .models import Contact
from .forms import ContactForm
import json
from django.http import QueryDict


#@login_required
@require_http_methods(['GET', 'POST'])
def contacts_all(req):

    payload = dict()
    status_code = 404
    if req.method == 'GET':
        contacts = serialize('json', Contact.objects.all())
        parsed_contacts = json.loads(contacts)

        contacts_formatted = list()
        for item in parsed_contacts:
            pk = item['pk']
            contact = item['fields']
            contact.update({'id': pk})
            contacts_formatted.append(contact)

        payload = {
            'contacts': contacts_formatted
        }
        status_code = 200
    elif req.method == 'POST':

        new_contact_values = json.loads(req.body)
        contact_dict = QueryDict('', mutable=True)
        contact_dict.update(new_contact_values)

        contact = ContactForm(contact_dict['contacts'] or None)

        if contact.is_valid():
            c = contact.save()
            status_code = 201
            payload = {
                'contacts':
                {
                    'id': c.pk,
                    'first_name': c.first_name,
                    'last_name': c.last_name,
                    'headshot_img': c.headshot_img
                }
            }
            print(payload)

    return JsonResponse(payload, content_type='application/json',
                        status=status_code)


#@login_required
@require_http_methods(['GET', 'DELETE', 'PATCH'])
def contact(req, contact_id):
    print('CHEGOOOOU:', req.method)
    if req.method == 'GET':
        contact = get_object_or_404(Contact, pk=contact_id)

    elif req.method == 'DELETE':
        contact = get_object_or_404(Contact, pk=contact_id)
        contact.delete()
        print('deleted')

    elif req.method == 'PATCH':
        contact = get_object_or_404(Contact, pk=contact_id)
        new_values = json.loads(req.body.decode('utf8'))['contacts']

        for key, value in new_values.items():
            try:
                contact.update_field(key, value)
            except AttributeError as e:
                status_code = 400
                error = str(e).replace('\'', '')
                payload = {
                    'errors:':
                    {
                        'message': error,
                        'httpResponse': status_code
                    }
                }
                return JsonResponse(payload, content_type='application/json',
                                    status=status_code)
        contact.save(update_fields=new_values.keys())

    payload = {
        'contacts':
        {
            'id': contact.pk,
            'first_name': contact.first_name,
            'last_name': contact.last_name,
            'headshot_img': contact.headshot_img
        }
    }
    return JsonResponse(payload, content_type='application/json', status=200)
