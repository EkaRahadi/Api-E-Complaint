from django.contrib import admin

from .models import rawComplaints, Complaint, Kategori, Status, Admin, Token

# Register your models here.
admin.site.register(rawComplaints)
admin.site.register(Complaint)
admin.site.register(Kategori)
admin.site.register(Status)
admin.site.register(Admin)
admin.site.register(Token)