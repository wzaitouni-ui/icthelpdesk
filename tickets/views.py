import json

from django import forms
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .kennisbank import CATEGORIEEN, CATEGORIEEN_EN, IMPACT, TREFWOORDEN, VRAGEN
from .models import Ticket
from .slack import meld_ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["medewerker", "categorie", "prioriteit", "probleem_beschrijving", "doorlopen_stappen"]


def chat_pagina(request):
    return render(request, "chat.html", {
        "intake": {
            "categorieen": CATEGORIEEN,
            "categorieen_en": CATEGORIEEN_EN,
            "trefwoorden": TREFWOORDEN,
            "vragen": VRAGEN,
            "impact": IMPACT,
        },
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
    beheer_url = request.build_absolute_uri(reverse("admin:tickets_ticket_change", args=[ticket.pk]))
    doorgestuurd = meld_ticket(ticket, beheer_url)
    return JsonResponse({"nummer": ticket.nummer, "doorgestuurd": doorgestuurd}, status=201)
