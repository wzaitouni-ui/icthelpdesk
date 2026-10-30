"""Lokale kennisbank en beslisboom voor de helpdesk-chat.

De boom bestaat uit knooppunten met een bericht en een aantal keuzes.
Een keuze verwijst naar een volgend knooppunt ("naar") of voert een actie
uit: "opgelost" sluit het gesprek af, "ticket" opent het ticketformulier.
De boom wordt als JSON aan de pagina meegegeven; er is geen externe API nodig.
"""

CATEGORIEEN = [
    ("wifi", "Wifi of internet"),
    ("wachtwoord", "Wachtwoord of inloggen"),
    ("printer", "Printer"),
    ("vpn", "VPN of thuiswerken"),
    ("email", "E-mail"),
    ("laptop", "Laptop traag of vastgelopen"),
    ("vergaderen", "Beeld of geluid bij vergaderen"),
    ("overig", "Iets anders"),
]

# Woorden waarmee een vrij getypte vraag aan een categorie wordt gekoppeld.
TREFWOORDEN = {
    "wifi": ["wifi", "wi-fi", "internet", "netwerk", "verbinding", "online", "offline", "router"],
    "wachtwoord": ["wachtwoord", "password", "inloggen", "login", "geblokkeerd", "vergeten", "account", "2fa", "authenticator", "code"],
    "printer": ["printer", "printen", "print", "afdrukken", "scannen", "scanner", "papier", "toner"],
    "vpn": ["vpn", "thuiswerken", "thuis", "op afstand", "remote"],
    "email": ["mail", "e-mail", "email", "inbox", "outlook", "gmail", "bijlage", "agenda"],
    "laptop": ["laptop", "computer", "pc", "traag", "langzaam", "vastgelopen", "hangt", "crash", "start niet", "opstarten", "update", "scherm", "blauw"],
    "vergaderen": ["teams", "meet", "zoom", "camera", "webcam", "microfoon", "geluid", "audio", "headset", "speaker", "vergadering", "beamer"],
}


def _stappenplan(categorie, stappen, prioriteit):
    """Maak een reeks knooppunten waarin elke stap eindigt met 'werkt het nu?'.

    Na de laatste mislukte stap wordt een ticket voorgesteld met de opgegeven
    prioriteit.
    """
    knopen = {}
    for i, tekst in enumerate(stappen, start=1):
        volgende = (
            {"label": "Werkt nog niet", "naar": f"{categorie}_{i + 1}"}
            if i < len(stappen)
            else {"label": "Werkt nog niet", "actie": "ticket", "prioriteit": prioriteit}
        )
        knopen[f"{categorie}_{i}"] = {
            "categorie": categorie,
            "stap": f"Stap {i} van {len(stappen)}",
            "tekst": tekst,
            "opties": [{"label": "Opgelost", "actie": "opgelost"}, volgende],
        }
    return knopen


BOOM = {
    "start": {
        "tekst": "Hoi! Ik ben de ICT-assistent. Waar loop je tegenaan? Kies een onderwerp of typ je probleem in je eigen woorden.",
        "opties": [
            {"label": "Wifi of internet", "naar": "wifi"},
            {"label": "Wachtwoord of inloggen", "naar": "wachtwoord"},
            {"label": "Printer", "naar": "printer"},
            {"label": "VPN of thuiswerken", "naar": "vpn_1"},
            {"label": "E-mail", "naar": "email_1"},
            {"label": "Laptop traag of vastgelopen", "naar": "laptop"},
            {"label": "Beeld of geluid bij vergaderen", "naar": "vergaderen_1"},
            {"label": "Iets anders", "actie": "ticket", "categorie": "overig", "prioriteit": "normaal"},
        ],
    },
    # Wifi: eerst uitzoeken of het een storing voor iedereen is.
    "wifi": {
        "categorie": "wifi",
        "tekst": "Heb alleen jij geen internet, of hebben collega's om je heen er ook last van?",
        "opties": [
            {"label": "Alleen ik", "naar": "wifi_1"},
            {"label": "Collega's ook", "naar": "wifi_storing"},
        ],
    },
    "wifi_storing": {
        "categorie": "wifi",
        "tekst": "Dan is het waarschijnlijk een storing op het netwerk zelf. Dat kun je niet zelf oplossen. Meld het direct, dan pakt ICT het met voorrang op.",
        "opties": [
            {"label": "Storing melden", "actie": "ticket", "prioriteit": "kritiek"},
        ],
    },
    **_stappenplan("wifi", [
        "Zet wifi op je apparaat uit, wacht tien seconden en zet het weer aan. Controleer ook of de vliegtuigmodus uit staat.",
        "Kijk of je met het juiste kantoornetwerk verbonden bent, en niet met een gastnetwerk of een netwerk van buren.",
        "Vergeet het netwerk in je wifi-instellingen en maak opnieuw verbinding. Je moet dan het wachtwoord opnieuw invullen.",
        "Start je laptop of telefoon volledig opnieuw op.",
    ], prioriteit="hoog"),
    # Wachtwoord: geblokkeerd account kan alleen ICT vrijgeven.
    "wachtwoord": {
        "categorie": "wachtwoord",
        "tekst": "Wat is er aan de hand?",
        "opties": [
            {"label": "Wachtwoord vergeten", "naar": "wachtwoord_1"},
            {"label": "Account geblokkeerd", "naar": "wachtwoord_geblokkeerd"},
            {"label": "Ik krijg geen inlogcode (2FA)", "naar": "wachtwoord_2fa"},
        ],
    },
    "wachtwoord_geblokkeerd": {
        "categorie": "wachtwoord",
        "tekst": "Na te vaak een verkeerd wachtwoord wordt je account tijdelijk geblokkeerd. Probeer niet opnieuw in te loggen, want dan blijft de blokkade staan. Wacht 15 minuten. Lukt het daarna nog niet, dan kan ICT je account vrijgeven.",
        "opties": [
            {"label": "Opgelost", "actie": "opgelost"},
            {"label": "Nog steeds geblokkeerd", "actie": "ticket", "prioriteit": "hoog"},
        ],
    },
    "wachtwoord_2fa": {
        "categorie": "wachtwoord",
        "tekst": "Controleer of de tijd op je telefoon automatisch wordt ingesteld; een afwijkende klok geeft ongeldige codes. Open daarna de authenticator-app opnieuw en gebruik een verse code. Nieuwe telefoon? Dan moet ICT je tweestapsverificatie opnieuw instellen.",
        "opties": [
            {"label": "Opgelost", "actie": "opgelost"},
            {"label": "Werkt nog niet", "actie": "ticket", "prioriteit": "hoog"},
        ],
    },
    **_stappenplan("wachtwoord", [
        "Ga naar het inlogscherm en klik op 'Wachtwoord vergeten'. Volg de stappen; je krijgt een code op je telefoon of privémail.",
        "Kies een nieuw wachtwoord van minimaal 12 tekens dat je nog niet eerder gebruikte. Log daarna overal opnieuw in, ook op je telefoon.",
    ], prioriteit="hoog"),
    # Printer
    "printer": {
        "categorie": "printer",
        "tekst": "Wat gebeurt er precies?",
        "opties": [
            {"label": "Er komt niets uit", "naar": "printer_1"},
            {"label": "Papierstoring of toner op", "naar": "printer_hardware"},
        ],
    },
    "printer_hardware": {
        "categorie": "printer",
        "tekst": "Volg de aanwijzingen op het schermpje van de printer; daar staat welke klep open moet. Trek vastgelopen papier er voorzichtig recht uit. Toner of papier op? Reserves liggen meestal naast de printer.",
        "opties": [
            {"label": "Opgelost", "actie": "opgelost"},
            {"label": "Printer blijft een fout geven", "actie": "ticket", "prioriteit": "normaal"},
        ],
    },
    **_stappenplan("printer", [
        "Controleer of je naar de juiste printer stuurt en of die aan staat, zonder foutmelding op het scherm.",
        "Open de afdrukwachtrij op je laptop, verwijder vastgelopen opdrachten en print opnieuw.",
        "Zet de printer uit, wacht 30 seconden en zet hem weer aan. Herstart ook je laptop.",
        "Controleer of je laptop met het kantoornetwerk verbonden is; buiten kantoor kun je meestal niet printen.",
    ], prioriteit="normaal"),
    **_stappenplan("vpn", [
        "Controleer eerst of je gewone internet werkt door een willekeurige website te openen.",
        "Sluit de VPN-app helemaal af en open hem opnieuw. Log daarna opnieuw in.",
        "Zit je op een openbaar netwerk, zoals in een hotel of trein? Die blokkeren soms VPN. Probeer de hotspot van je telefoon.",
        "Herstart je laptop en maak opnieuw verbinding met de VPN.",
    ], prioriteit="hoog"),
    **_stappenplan("email", [
        "Kijk of je mail via de browser (webmail) wel werkt. Zo ja, dan zit het probleem in de app op je laptop of telefoon.",
        "Sluit de mail-app volledig af en open hem opnieuw. Controleer of je nog online bent.",
        "Is je mailbox vol? Leeg de prullenbak en verwijder grote bijlagen uit verzonden items.",
        "Kijk in je map Spam of Ongewenst als je een verwachte mail niet ontvangt.",
    ], prioriteit="normaal"),
    # Laptop: niet opstarten is ernstiger dan traag.
    "laptop": {
        "categorie": "laptop",
        "tekst": "Wat is het probleem met je laptop?",
        "opties": [
            {"label": "Traag of programma hangt", "naar": "laptop_1"},
            {"label": "Start niet op", "naar": "laptop_start"},
            {"label": "Gevallen of schade", "actie": "ticket", "prioriteit": "hoog"},
        ],
    },
    "laptop_start": {
        "categorie": "laptop",
        "tekst": "Sluit de oplader aan en wacht vijf minuten. Houd daarna de aan-knop 15 seconden ingedrukt en start opnieuw. Brandt er een lampje bij de oplaadpoort?",
        "opties": [
            {"label": "Opgelost", "actie": "opgelost"},
            {"label": "Start nog steeds niet", "actie": "ticket", "prioriteit": "hoog"},
        ],
    },
    **_stappenplan("laptop", [
        "Sla je werk op en sluit programma's die je niet gebruikt, vooral browsertabbladen.",
        "Start je laptop opnieuw op via 'Opnieuw opstarten', niet via de klep dichtdoen.",
        "Kijk of er updates klaarstaan en installeer ze. Laat de laptop daarna aan de oplader staan tot het klaar is.",
        "Controleer of je schijf bijna vol is en verwijder of archiveer grote bestanden in je downloads.",
    ], prioriteit="normaal"),
    **_stappenplan("vergaderen", [
        "Controleer in de vergader-app bij instellingen of de juiste camera, microfoon en speaker gekozen zijn.",
        "Kijk of je microfoon of camera niet gedempt is in de app, op je headset of met een schuifje op je laptop.",
        "Sluit andere apps die je camera of microfoon kunnen gebruiken en verlaat de vergadering. Neem daarna opnieuw deel.",
        "Gebruik je een headset of dock? Haal de kabel eruit en sluit hem opnieuw aan, of probeer een andere poort.",
    ], prioriteit="normaal"),
}
