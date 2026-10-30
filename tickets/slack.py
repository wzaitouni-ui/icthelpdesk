"""Meldingen naar Slack via een Incoming Webhook (geen extra pakketten nodig)."""

import json
import logging
import urllib.error
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

PRIORITEIT_ICOON = {
    "kritiek": ":red_circle:",
    "hoog": ":large_orange_circle:",
    "normaal": ":large_yellow_circle:",
    "laag": ":large_green_circle:",
}


def _veilig(tekst):
    # Voorkomt dat tekst van medewerkers als Slack-opmaak, link of @channel wordt gelezen.
    return tekst.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _tags():
    tags = []
    for waarde in settings.SLACK_TAG.split(","):
        waarde = waarde.strip()
        if waarde in ("channel", "here"):
            tags.append(f"<!{waarde}>")
        elif waarde.startswith("S"):
            tags.append(f"<!subteam^{waarde}>")
        elif waarde.startswith(("U", "W")):
            tags.append(f"<@{waarde}>")
    return " ".join(tags)


def bericht_voor(ticket, beheer_url):
    prioriteit = ticket.get_prioriteit_display().split(" - ")[0]
    regels = []
    if tags := _tags():
        regels.append(tags)
    regels.append(
        f"{PRIORITEIT_ICOON.get(ticket.prioriteit, '')} *Nieuwe ICT-melding {ticket.nummer}*"
        f"  ·  {prioriteit}  ·  {ticket.get_categorie_display()}"
    )
    regels.append(f"*Van:* {_veilig(ticket.medewerker)}")
    regels.append(f"*Melding:* {_veilig(ticket.probleem_beschrijving)}")
    regels += [f"• {_veilig(r)}" for r in ticket.doorlopen_stappen.splitlines() if r.strip()]
    regels.append(f"<{beheer_url}|Open in beheer>")
    return "\n".join(regels)


def meld_ticket(ticket, beheer_url):
    """Stuur het ticket naar Slack. Geeft False terug als dat niet lukt; het ticket blijft dan gewoon opgeslagen."""
    if not settings.SLACK_WEBHOOK_URL:
        logger.warning("SLACK_WEBHOOK_URL is niet ingesteld; %s niet naar Slack gestuurd.", ticket.nummer)
        return False

    verzoek = urllib.request.Request(
        settings.SLACK_WEBHOOK_URL,
        data=json.dumps({"text": bericht_voor(ticket, beheer_url)}).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(verzoek, timeout=5) as antwoord:
            return antwoord.status == 200
    except (urllib.error.URLError, OSError):
        logger.exception("Slack-melding voor %s mislukt.", ticket.nummer)
        return False
