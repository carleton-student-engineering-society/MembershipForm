from django.contrib import admin
from .models import CarletonEmail, Membership, MembershipUpdateHistory

class CarletonEmailAdmin(admin.ModelAdmin):
    list_display = ["user"]

admin.site.register(CarletonEmail, CarletonEmailAdmin)

class MembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "signup_date", "year"]

admin.site.register(Membership, MembershipAdmin)

class MembershipUpdateHistoryAdmin(admin.ModelAdmin):
    list_display = ["membership__user", "change_user", "change_date"]

admin.site.register(MembershipUpdateHistory, MembershipUpdateHistoryAdmin)

