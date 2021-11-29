from django.contrib import admin
from .models import CatalogueEntries, GraphEntries, SubmittedCatelogueEntries
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render

# Register your models here.
admin.site.register(CatalogueEntries)
admin.site.register(GraphEntries)


def send_msg(request, recepient, file, accepted=True):
    if request.method == 'POST':
        if accepted:
            subject = 'Your annotation is accepted: '+ file
            message = 'Congratulations! Your annotation has been accepted.'
            send_mail(subject,
                message, settings.EMAIL_HOST_USER, [recepient], fail_silently=False)
        else:
            subject = 'Your annotation is rejected: '+ file
            message = 'Sorry! Your annotation has been rejected'
            send_mail(subject,
                      message, settings.EMAIL_HOST_USER, [recepient], fail_silently=False)


@admin.action(description='send confirmation email and change status')
def approve(modeladmin, request, queryset):
    queryset.update(status='a')
    for entry in queryset:
        send_msg(request, entry.user_email, entry.docfile.name)


@admin.action(description='send rejection email and change status')
def reject(modeladmin, request, queryset):
    queryset.update(status='r')
    for entry in queryset:
        send_msg(request, entry.user_email, entry.docfile.name, accepted=False)


class SubmittedCatelogueEntriesAdmin(admin.ModelAdmin):
    list_display = ['docfile', 'user_email', 'username', 'status']
    ordering = ['docfile']
    actions = [approve, reject]

admin.site.register(SubmittedCatelogueEntries, SubmittedCatelogueEntriesAdmin)
