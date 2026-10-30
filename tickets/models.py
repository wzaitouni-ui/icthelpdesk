from django.db import models

from .kennisbank import CATEGORIEEN


class Ticket(models.Model):
    class Prioriteit(models.TextChoices):
        LAAG = "laag", "Laag - kan wachten"
        NORMAAL = "normaal", "Normaal - ik kan nog werken"
        HOOG = "hoog", "Hoog - ik kan niet werken"
        KRITIEK = "kritiek", "Kritiek - meerdere collega's getroffen"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_BEHANDELING = "in_behandeling", "In behandeling"
        WACHT_OP_MEDEWERKER = "wacht_op_medewerker", "Wacht op medewerker"
        OPGELOST = "opgelost", "Opgelost"
        GESLOTEN = "gesloten", "Gesloten"

    medewerker = models.CharField("naam", max_length=100)
    email = models.EmailField("e-mail", blank=True)
    categorie = models.CharField(max_length=20, choices=CATEGORIEEN, default="overig")
    prioriteit = models.CharField(max_length=10, choices=Prioriteit.choices, default=Prioriteit.NORMAAL)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.OPEN)
    probleem_beschrijving = models.TextField("omschrijving")
    doorlopen_stappen = models.TextField(blank=True, help_text="Wat de medewerker al in de chat heeft geprobeerd.")
    datum = models.DateTimeField("aangemaakt", auto_now_add=True)
    bijgewerkt = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-datum"]

    @property
    def nummer(self):
        return f"HD-{self.pk:04d}"

    def __str__(self):
        return f"{self.nummer} {self.medewerker}: {self.probleem_beschrijving[:30]}"
