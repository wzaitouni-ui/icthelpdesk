import json
import os

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import anthropic
from .models import Ticket

def chat_pagina(request):
    return render(request, "chat.html")

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        bericht = data.get("bericht", "")

        systeem_instructie = (
            "Je bent een vriendelijke IT-helpdesk assistent. "
            "Probeer het probleem van de collega in 1 of 2 korte zinnen te verhelpen als het iets simpels is "
            "(bijvoorbeeld herstarten, kabel controleren, wachtwoord resetten via portaal). "
            "Als het probleem te ingewikkeld is, hardware kapot is, of rechten vereist, "
            "antwoord dan exact en alleen met het woord: ESCALATIE"
        )

        try:
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            response = client.messages.create(
                model="claude-haiku-5-5",
                max_tokens=1024,
                output_config={"effort": "low"},
                system=systeem_instructie,
                messages=[
                    {"role": "user", "content": bericht}
                ]
            )
            antwoord = "".join(b.text for b in response.content if b.type == "text").strip()

            if "ESCALATIE" in antwoord:
                Ticket.objects.create(
                    medewerker="Collega",
                    probleem_beschrijving=bericht,
                    status="Open - Geëscaleerd naar ICT"
                )
                return JsonResponse({"antwoord": "Dit probleem vereist de IT-beheerder. Ik heb direct een ticket aangemaakt!"})

            return JsonResponse({"antwoord": antwoord})
        except Exception as e:
            return JsonResponse({"antwoord": f"Fout bij verbinden met AI: {str(e)}"})

    return JsonResponse({"fout": "Alleen POST toegestaan"}, status=400)
