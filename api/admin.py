from django.contrib import admin
from .models import Review,UrlStream,CredentialStream,ApiKeyStream,Notification, Payment, Tour, Country, City

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('date', 'source_stream', 'rating', 'sentiment')
    list_filter = ('source_stream', 'sentiment')
    search_fields = ('review_text',)

admin.site.register(UrlStream)
admin.site.register(CredentialStream)
admin.site.register(ApiKeyStream)
admin.site.register(Notification)
admin.site.register(Payment)
admin.site.register(City)
admin.site.register(Country)
admin.site.register(Tour)