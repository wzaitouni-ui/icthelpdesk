import json

from django.test import Client, TestCase
from django.urls import reverse

from .kennisbank import BOOM, CATEGORIEEN, TREFWOORDEN
from .models import Ticket

CATEGORIE_CODES = {code for code, _ in CATEGORIEEN}
PRIORITEIT_CODES = set(Ticket.Prioriteit.values)


class KennisbankTests(TestCase):
    def test_alle_verwijzingen_bestaan(self):
        for id, knoop in BOOM.items():
            for optie in knoop["opties"]:
                if "naar" in optie:
                    self.assertIn(optie["naar"], BOOM, f"{id} verwijst naar onbekend knooppunt")
                else:
                    self.assertIn(optie["actie"], {"opgelost", "ticket"}, id)

    def test_tickets_gebruiken_geldige_waarden(self):
        for id, knoop in BOOM.items():
            for optie in knoop["opties"]:
                if optie.get("actie") == "ticket":
                    self.assertIn(optie["prioriteit"], PRIORITEIT_CODES, id)
                    self.assertIn(optie.get("categorie", knoop.get("categorie")), CATEGORIE_CODES, id)

    def test_elke_categorie_met_trefwoorden_heeft_een_startpunt(self):
        for categorie in TREFWOORDEN:
            self.assertTrue(categorie in BOOM or f"{categorie}_1" in BOOM, categorie)
            self.assertTrue(
                any(o.get("naar", "").startswith(categorie) for o in BOOM["start"]["opties"]),
                categorie,
            )


class HelpdeskViewTests(TestCase):
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def csrf_token(self):
        self.client.get(reverse("home"))
        return self.client.cookies["csrftoken"].value

    def post_ticket(self, data, token=None):
        return self.client.post(
            reverse("ticket_aanmaken"),
            data=json.dumps(data),
            content_type="application/json",
            headers={"X-CSRFToken": token or self.csrf_token()},
        )

    def test_homepage_toont_chat(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="kennisbank"')
        self.assertContains(response, "Ticket aanmaken")

    def test_ticket_wordt_opgeslagen(self):
        response = self.post_ticket({
            "medewerker": "Sam",
            "email": "sam@example.com",
            "categorie": "printer",
            "prioriteit": "hoog",
            "probleem_beschrijving": "Printer op de tweede verdieping print niets.",
            "doorlopen_stappen": "Stap 1 van 4: ... → Werkt nog niet",
        })
        self.assertEqual(response.status_code, 201)
        ticket = Ticket.objects.get()
        self.assertEqual(response.json()["nummer"], ticket.nummer)
        self.assertEqual(ticket.status, Ticket.Status.OPEN)
        self.assertEqual(ticket.prioriteit, "hoog")
        self.assertEqual(ticket.categorie, "printer")

    def test_ongeldig_ticket_geeft_veldfouten(self):
        response = self.post_ticket({"medewerker": "", "prioriteit": "supersnel", "probleem_beschrijving": ""})
        self.assertEqual(response.status_code, 400)
        fouten = response.json()["fouten"]
        self.assertIn("medewerker", fouten)
        self.assertIn("prioriteit", fouten)
        self.assertIn("probleem_beschrijving", fouten)
        self.assertFalse(Ticket.objects.exists())

    def test_zonder_csrf_token_geweigerd(self):
        response = self.client.post(
            reverse("ticket_aanmaken"),
            data=json.dumps({"medewerker": "Sam", "probleem_beschrijving": "x"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_alleen_post(self):
        self.assertEqual(self.client.get(reverse("ticket_aanmaken")).status_code, 405)
