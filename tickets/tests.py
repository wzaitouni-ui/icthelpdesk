import json
import urllib.error
from unittest import mock

from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .kennisbank import CATEGORIEEN, IMPACT, TREFWOORDEN, VRAGEN
from .models import Ticket
from .slack import bericht_voor

CATEGORIE_CODES = {code for code, _ in CATEGORIEEN}
PRIORITEIT_CODES = set(Ticket.Prioriteit.values)
WEBHOOK = "https://hooks.slack.com/services/T000/B000/test"


class IntakeTests(TestCase):
    def test_elke_categorie_heeft_vragen(self):
        self.assertEqual(set(VRAGEN), CATEGORIE_CODES)
        self.assertTrue(set(TREFWOORDEN) <= CATEGORIE_CODES)

    def test_prioriteiten_zijn_geldig(self):
        opties = [o for vragen in VRAGEN.values() for v in vragen for o in v["opties"]] + IMPACT["opties"]
        for optie in opties:
            if "prioriteit" in optie:
                self.assertIn(optie["prioriteit"], PRIORITEIT_CODES, optie)
        self.assertTrue(all("prioriteit" in o for o in IMPACT["opties"]))


class SlackBerichtTests(TestCase):
    @override_settings(SLACK_TAG="")
    def test_tekst_van_medewerker_wordt_onschadelijk_gemaakt(self):
        ticket = Ticket.objects.create(
            medewerker="Sam <!channel>",
            categorie="printer",
            prioriteit="hoog",
            probleem_beschrijving="Printer <https://evil.example|klik> & kapot",
            doorlopen_stappen="Wat gebeurt er? Er komt niets uit",
        )
        tekst = bericht_voor(ticket, "https://helpdesk.example/admin/tickets/ticket/1/change/")
        self.assertIn(ticket.nummer, tekst)
        self.assertIn("Sam &lt;!channel&gt;", tekst)
        self.assertNotIn("<!channel>", tekst)
        self.assertNotIn("<https://evil", tekst)
        self.assertIn("&amp; kapot", tekst)
        self.assertIn("• Wat gebeurt er? Er komt niets uit", tekst)
        self.assertIn("<https://helpdesk.example/admin/tickets/ticket/1/change/|Open in beheer>", tekst)

    def test_tags(self):
        ticket = Ticket.objects.create(medewerker="Sam", probleem_beschrijving="x")
        gevallen = {
            "channel": "<!channel>\n",
            "here": "<!here>\n",
            "S0ITBEHEER": "<!subteam^S0ITBEHEER>\n",
            "U111, U222": "<@U111> <@U222>\n",
        }
        for instelling, begin in gevallen.items():
            with self.settings(SLACK_TAG=instelling):
                self.assertTrue(bericht_voor(ticket, "https://x").startswith(begin), instelling)
        with self.settings(SLACK_TAG=""):
            self.assertTrue(bericht_voor(ticket, "https://x").startswith(":"))


class HelpdeskViewTests(TestCase):
    MELDING = {
        "medewerker": "Sam",
        "categorie": "printer",
        "prioriteit": "hoog",
        "probleem_beschrijving": "Printer op de tweede verdieping print niets.",
        "doorlopen_stappen": "Wat gebeurt er? Er komt niets uit",
    }

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)

    def post_ticket(self, data):
        self.client.get(reverse("home"))
        return self.client.post(
            reverse("ticket_aanmaken"),
            data=json.dumps(data),
            content_type="application/json",
            headers={"X-CSRFToken": self.client.cookies["csrftoken"].value},
        )

    def test_homepage_toont_intake(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="intake"')

    @override_settings(SLACK_WEBHOOK_URL=WEBHOOK)
    @mock.patch("tickets.slack.urllib.request.urlopen")
    def test_ticket_wordt_opgeslagen_en_naar_slack_gestuurd(self, urlopen):
        urlopen.return_value.__enter__.return_value.status = 200
        response = self.post_ticket(self.MELDING)

        self.assertEqual(response.status_code, 201)
        ticket = Ticket.objects.get()
        self.assertEqual(response.json(), {"nummer": ticket.nummer, "doorgestuurd": True})
        self.assertEqual(ticket.status, Ticket.Status.OPEN)

        verzoek = urlopen.call_args.args[0]
        self.assertEqual(verzoek.full_url, WEBHOOK)
        tekst = json.loads(verzoek.data)["text"]
        self.assertIn(ticket.nummer, tekst)
        self.assertIn(f"/admin/tickets/ticket/{ticket.pk}/change/", tekst)

    @override_settings(SLACK_WEBHOOK_URL=WEBHOOK)
    @mock.patch("tickets.slack.urllib.request.urlopen", side_effect=urllib.error.URLError("down"))
    def test_slack_storing_blokkeert_ticket_niet(self, urlopen):
        response = self.post_ticket(self.MELDING)
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.json()["doorgestuurd"])
        self.assertEqual(Ticket.objects.count(), 1)

    @override_settings(SLACK_WEBHOOK_URL="")
    @mock.patch("tickets.slack.urllib.request.urlopen")
    def test_zonder_webhook_geen_slack_aanroep(self, urlopen):
        response = self.post_ticket(self.MELDING)
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.json()["doorgestuurd"])
        urlopen.assert_not_called()

    def test_ongeldige_melding_geeft_veldfouten(self):
        response = self.post_ticket({"medewerker": "", "prioriteit": "supersnel", "probleem_beschrijving": ""})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()["fouten"]), {"medewerker", "categorie", "prioriteit", "probleem_beschrijving"})
        self.assertFalse(Ticket.objects.exists())

    def test_zonder_csrf_token_geweigerd(self):
        response = self.client.post(
            reverse("ticket_aanmaken"), data=json.dumps(self.MELDING), content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

    def test_alleen_post(self):
        self.assertEqual(self.client.get(reverse("ticket_aanmaken")).status_code, 405)
