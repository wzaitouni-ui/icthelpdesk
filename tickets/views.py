import json

from django import forms
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .kennisbank import BOOM, CATEGORIEEN, TREFWOORDEN
from .models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["medewerker", "email", "categorie", "prioriteit", "probleem_beschrijving", "doorlopen_stappen"]


def chat_pagina(request):
    return render(request, "chat.html", {
        "kennisbank": {"boom": BOOM, "trefwoorden": TREFWOORDEN},
        "categorieen": CATEGORIEEN,
        "prioriteiten": Ticket.Prioriteit.choices,
    })


@require_POST
def ticket_aanmaken(request):
    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"fouten": {"__all__": ["Ongeldige aanvraag."]}}, status=400)

    form = TicketForm(data)
    if not form.is_valid():
        fouten = {veld: [str(f) for f in lijst] for veld, lijst in form.errors.items()}
        return JsonResponse({"fouten": fouten}, status=400)

    ticket = form.save()
    return JsonResponse({"nummer": ticket.nummer, "prioriteit": ticket.get_prioriteit_display()}, status=201)
