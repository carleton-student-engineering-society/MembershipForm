from django.contrib import admin
from .models import CarletonEmail, Membership

class CarletonEmailAdmin(admin.ModelAdmin):
    list_display = ["user"]

admin.site.register(CarletonEmail, CarletonEmailAdmin)

class MembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "signup_date", "year"]

admin.site.register(Membership, MembershipAdmin)