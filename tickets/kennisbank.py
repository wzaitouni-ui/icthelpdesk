"""Korte intakevragen voor de helpdesk-chat.

De chat lost niets zelf op: hij stelt per onderwerp een paar meerkeuzevragen
zodat de ICT-beheerder in één oogopslag ziet waar het om gaat, en stuurt de
melding daarna door. Een antwoord met "prioriteit" zet de prioriteit direct
(bijv. een storing voor meerdere collega's) en slaat de impactvraag over.
"""

CATEGORIEEN = [
    ("wifi", "Wifi of internet"),
    ("wachtwoord", "Wachtwoord of inloggen"),
    ("printer", "Printer"),
    ("vpn", "VPN of thuiswerken"),
    ("email", "E-mail"),
    ("laptop", "Laptop of computer"),
    ("vergaderen", "Beeld of geluid bij vergaderen"),
    ("overig", "Iets anders"),
]

# Woorden waarmee een vrij getypte melding aan een onderwerp wordt gekoppeld.
TREFWOORDEN = {
    "wifi": ["wifi", "wi-fi", "internet", "netwerk", "verbinding", "online", "offline", "router"],
    "wachtwoord": ["wachtwoord", "password", "inloggen", "login", "geblokkeerd", "vergeten", "account", "2fa", "authenticator", "code"],
    "printer": ["printer", "printen", "print", "afdrukken", "scannen", "scanner", "papier", "toner"],
    "vpn": ["vpn", "thuiswerken", "thuis", "op afstand", "remote"],
    "email": ["mail", "e-mail", "email", "inbox", "outlook", "gmail", "bijlage", "agenda"],
    "laptop": ["laptop", "computer", "pc", "traag", "langzaam", "vastgelopen", "hangt", "crash", "start niet", "opstarten", "update", "scherm", "toetsenbord"],
    "vergaderen": ["teams", "meet", "zoom", "camera", "webcam", "microfoon", "geluid", "audio", "headset", "speaker", "vergadering", "beamer"],
}


def _opties(*labels):
    return [{"label": label} for label in labels]


VRAGEN = {
    "wifi": [
        {"vraag": "Heb alleen jij er last van, of collega's ook?", "opties": [
            {"label": "Alleen ik"},
            {"label": "Collega's ook", "prioriteit": "kritiek"},
        ]},
    ],
    "wachtwoord": [
        {"vraag": "Wat is er aan de hand?", "opties": _opties(
            "Wachtwoord vergeten", "Account geblokkeerd", "Geen inlogcode (2FA)", "Iets anders")},
    ],
    "printer": [
        {"vraag": "Wat gebeurt er?", "opties": _opties(
            "Er komt niets uit", "Papierstoring", "Toner of papier op", "Slechte afdruk", "Scannen lukt niet")},
    ],
    "vpn": [
        {"vraag": "Wat gebeurt er?", "opties": _opties(
            "Kan niet verbinden", "Verbinding valt steeds weg", "Ik heb nog geen VPN")},
    ],
    "email": [
        {"vraag": "Wat gaat er mis?", "opties": _opties(
            "Ik ontvang geen mail", "Ik kan niet versturen", "Mail-app werkt niet", "Agenda of gedeelde mailbox")},
    ],
    "laptop": [
        {"vraag": "Wat is er met je laptop?", "opties": _opties(
            "Traag", "Vastgelopen", "Start niet op", "Schade of gevallen", "Scherm of toetsenbord")},
    ],
    "vergaderen": [
        {"vraag": "Wat werkt er niet?", "opties": _opties(
            "Camera", "Microfoon", "Geluid", "Scherm delen", "Vergaderscherm of beamer")},
    ],
    "overig": [],
}

IMPACT = {"vraag": "Hoe erg is het?", "opties": [
    {"label": "Ik kan niet werken", "prioriteit": "hoog"},
    {"label": "Lastig, maar ik kan verder", "prioriteit": "normaal"},
    {"label": "Kan wachten", "prioriteit": "laag"},
]}
