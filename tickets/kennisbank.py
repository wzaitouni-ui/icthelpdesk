"""Korte intakevragen voor de helpdesk-chat, in het Nederlands en Engels.

De chat lost niets zelf op: hij stelt per onderwerp een paar meerkeuzevragen
zodat de ICT-beheerder in één oogopslag ziet waar het om gaat, en stuurt de
melding daarna door. Een antwoord met "prioriteit" zet de prioriteit direct
(bijv. een storing voor meerdere collega's) en slaat de impactvraag over.

De medewerker ziet de vragen in zijn eigen taal; het ticket en de Slack-melding
krijgen altijd de Nederlandse tekst, zodat de beheerder elke melding kan lezen.
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

CATEGORIEEN_EN = {
    "wifi": "Wi-Fi or internet",
    "wachtwoord": "Password or login",
    "printer": "Printer",
    "vpn": "VPN or working from home",
    "email": "Email",
    "laptop": "Laptop or computer",
    "vergaderen": "Audio or video in meetings",
    "overig": "Something else",
}

# Woorden waarmee een vrij getypte melding aan een onderwerp wordt gekoppeld.
TREFWOORDEN = {
    "wifi": ["wifi", "wi-fi", "internet", "netwerk", "network", "verbinding", "connection", "online", "offline", "router", "wireless"],
    "wachtwoord": ["wachtwoord", "password", "inloggen", "login", "log in", "sign in", "geblokkeerd", "locked", "vergeten", "forgot", "account", "2fa", "authenticator", "code"],
    "printer": ["printer", "printen", "print", "afdrukken", "scannen", "scan", "papier", "paper", "toner"],
    "vpn": ["vpn", "thuiswerken", "thuis", "home", "op afstand", "remote"],
    "email": ["mail", "e-mail", "email", "inbox", "outlook", "gmail", "bijlage", "attachment", "agenda", "calendar"],
    "laptop": ["laptop", "computer", "pc", "traag", "langzaam", "slow", "vastgelopen", "frozen", "hangt", "crash", "start niet", "opstarten", "boot", "update", "scherm", "screen", "toetsenbord", "keyboard"],
    "vergaderen": ["teams", "meet", "zoom", "camera", "webcam", "microfoon", "microphone", "mic", "geluid", "sound", "audio", "headset", "speaker", "vergadering", "meeting", "beamer"],
}


def _optie(nl, en, prioriteit=None):
    optie = {"label": nl, "label_en": en}
    if prioriteit:
        optie["prioriteit"] = prioriteit
    return optie


VRAGEN = {
    "wifi": [
        {"vraag": "Heb alleen jij er last van, of collega's ook?",
         "vraag_en": "Is it just you, or are colleagues affected too?",
         "opties": [
             _optie("Alleen ik", "Just me"),
             _optie("Collega's ook", "Colleagues too", prioriteit="kritiek"),
         ]},
    ],
    "wachtwoord": [
        {"vraag": "Wat is er aan de hand?", "vraag_en": "What's going on?", "opties": [
            _optie("Wachtwoord vergeten", "Forgot my password"),
            _optie("Account geblokkeerd", "Account locked"),
            _optie("Geen inlogcode (2FA)", "No login code (2FA)"),
            _optie("Iets anders", "Something else"),
        ]},
    ],
    "printer": [
        {"vraag": "Wat gebeurt er?", "vraag_en": "What's happening?", "opties": [
            _optie("Er komt niets uit", "Nothing prints"),
            _optie("Papierstoring", "Paper jam"),
            _optie("Toner of papier op", "Out of toner or paper"),
            _optie("Slechte afdruk", "Poor print quality"),
            _optie("Scannen lukt niet", "Scanning doesn't work"),
        ]},
    ],
    "vpn": [
        {"vraag": "Wat gebeurt er?", "vraag_en": "What's happening?", "opties": [
            _optie("Kan niet verbinden", "Can't connect"),
            _optie("Verbinding valt steeds weg", "Connection keeps dropping"),
            _optie("Ik heb nog geen VPN", "I don't have VPN yet"),
        ]},
    ],
    "email": [
        {"vraag": "Wat gaat er mis?", "vraag_en": "What's going wrong?", "opties": [
            _optie("Ik ontvang geen mail", "I'm not receiving email"),
            _optie("Ik kan niet versturen", "I can't send email"),
            _optie("Mail-app werkt niet", "Mail app isn't working"),
            _optie("Agenda of gedeelde mailbox", "Calendar or shared mailbox"),
        ]},
    ],
    "laptop": [
        {"vraag": "Wat is er met je laptop?", "vraag_en": "What's wrong with your laptop?", "opties": [
            _optie("Traag", "Slow"),
            _optie("Vastgelopen", "Frozen"),
            _optie("Start niet op", "Won't start"),
            _optie("Schade of gevallen", "Damaged or dropped"),
            _optie("Scherm of toetsenbord", "Screen or keyboard"),
        ]},
    ],
    "vergaderen": [
        {"vraag": "Wat werkt er niet?", "vraag_en": "What isn't working?", "opties": [
            _optie("Camera", "Camera"),
            _optie("Microfoon", "Microphone"),
            _optie("Geluid", "Sound"),
            _optie("Scherm delen", "Screen sharing"),
            _optie("Vergaderscherm of beamer", "Meeting room screen or projector"),
        ]},
    ],
    "overig": [],
}

IMPACT = {"vraag": "Hoe erg is het?", "vraag_en": "How bad is it?", "opties": [
    _optie("Ik kan niet werken", "I can't work", prioriteit="hoog"),
    _optie("Lastig, maar ik kan verder", "Annoying, but I can keep working", prioriteit="normaal"),
    _optie("Kan wachten", "It can wait", prioriteit="laag"),
]}
