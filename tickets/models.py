from django.db import models

class Ticket(models.Model):
    medewerker = models.CharField(max_length=100, default="Collega")
    probleem_beschrijving = models.TextField()
    status = models.CharField(max_length=50, default="Geëscaleerd naar ICT")
    datum = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medewerker}: {self.probleem_beschrijving[:30]}"