from django.contrib import admin

# from django.contrib.auth.admin import UserAdmin as OldUserAdmin
# from django.contrib.auth.models import User

# from models import User

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
# class ParticipantInline(admin.StackedInline):
#     model = Participant
#     can_delete = False
#     verbose_name_plural = 'participant'


# Define a new User admin
# class UserAdmin(OldUserAdmin):
#     inlines = (ParticipantInline, )

# Re-register UserAdmin
# admin.site.unregister(User)
# admin.site.register(User, UserAdmin)
