from django.contrib import admin
from .models import Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("nummer", "medewerker", "categorie", "prioriteit", "status", "datum")
    list_editable = ("prioriteit", "status")
    list_filter = ("status", "prioriteit", "categorie")
    search_fields = ("medewerker", "email", "probleem_beschrijving")
    readonly_fields = ("doorlopen_stappen", "datum", "bijgewerkt")
