from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from authentication.models import User, Company
from django.conf import settings

VIATOR = 1
AIRBNB = 2
TRIPADVISOR = 3
EXPEDIA = 4
KLOOK = 5
CIVITAS = 6
GETYOURGUIDE = 7
FACEBOOK = 8
GOOGLE = 9
INSTAGRAM = 10
LINKEDIN = 11



STREAM_CHOICES = (
    (VIATOR, 'viator'),
    (AIRBNB, 'airbnb'),
    (TRIPADVISOR, 'tripadvisor'),
    (EXPEDIA, 'expedia'),
    (KLOOK, 'klook'),
    (CIVITAS, 'civitatis'),
    (GETYOURGUIDE, 'getyourguide'),
    (FACEBOOK, 'facebook'),
    (GOOGLE, 'google'),
    (INSTAGRAM, 'instagram'),
    (LINKEDIN, 'linkedin'),
)

SOURCE_STREAM = {
    VIATOR: {
        "id": VIATOR,
        "name": "Viator",
        "template_name": "viator",
        "url": "www.viator.com/",
        "seller": "Viator",
        "logo_path": "static/stream_logos/viator.png"
    },
    AIRBNB: {
        "id": AIRBNB,
        "name": "Airbnb",
        "template_name": "airbnb",
        "url": "www.airbnb.com/",
        "seller": "Airbnb",
        "logo_path": "static/stream_logos/airbnb.png"
    },
    TRIPADVISOR: {
        "id": TRIPADVISOR,
        "name": "TripAdvisor",
        "template_name": "tripadvisor",
        "url": "www.tripadvisor.com/",
        "seller": "TripAdvisor",
        "logo_path": "static/stream_logos/tripadvisor.png"
    },
    EXPEDIA: {
        "id": EXPEDIA,
        "name": "Expedia",
        "template_name": "expedia",
        "url": "www.expedia.com/",
        "seller": "Expedia",
        "logo_path": "static/stream_logos/expedia.png"
    },
    KLOOK: {
        "id": KLOOK,
        "name": "Klook",
        "template_name": "klook",
        "url": "www.klook.com/",
        "seller": "Klook",
        "logo_path": "static/stream_logos/klook.png"
    },
    CIVITAS: {
        "id": CIVITAS,
        "name": "Civitatis",
        "template_name": "civitatis",
        "url": "www.civitatis.com/",
        "seller": "Civitatis",
        "logo_path": "static/stream_logos/civitas.png"
    },
    GETYOURGUIDE: {
        "id": GETYOURGUIDE,
        "name": "GetYourGuide",
        "template_name": "getyourguide",
        "url": "www.getyourguide.com/",
        "seller": "GetYourGuide",
        "logo_path": "static/stream_logos/getyourguide.png"
    },
    FACEBOOK: {
        "id": FACEBOOK,
        "name": "Facebook",
        "template_name": "facebook",
        "url": "www.facebook.com/",
        "seller": "Facebook",
        "logo_path": "static/stream_logos/facebook.png"
    },
    GOOGLE: {
        "id": GOOGLE,
        "name": "Google",
        "template_name": "google",
        "url": "www.google.com/",
        "seller": "Google",
        "logo_path": "static/stream_logos/google.png"
    },
    INSTAGRAM: {
        "id": INSTAGRAM,
        "name": "Instagram",
        "template_name": "instagram",
        "url": "www.instagram.com/",
        "seller": "Instagram",
        "logo_path": "static/stream_logos/instagram.png"
    },
    LINKEDIN: {
        "id": LINKEDIN,
        "name": "LinkedIn",
        "template_name": "linkedin",
        "url": "www.linkedin.com/",
        "seller": "LinkedIn",
        "logo_path": "static/stream_logos/linkedin.png"
    }
}

class StandardCopyEmailAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=100)


class Review(models.Model):
    POSITIVE = 3
    NEUTRAL = 2
    NEGATIVE = 1

    SENTIMENT_CHOICES = (
        (POSITIVE, 'Positive'),
        (NEUTRAL, 'Neutral'),
        (NEGATIVE, 'Negative'),
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE,null=True)
    date = models.DateField(null=True, blank=True)
    source_stream = models.PositiveSmallIntegerField(choices=STREAM_CHOICES)
    review_text = models.TextField(null=True, blank=True)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
    sentiment = models.PositiveSmallIntegerField(choices=SENTIMENT_CHOICES, null=True)
    review_url = models.TextField(null=True)
    ai_checked = models.BooleanField(default=False)
    responded = models.BooleanField(default=False)
    product_id = models.CharField(max_length=255, null=True)
    product = models.CharField(max_length=255, null=True)
    country_code = models.CharField(max_length=255, null=True)
    places = models.TextField(null=True)
    img = models.TextField(null=True)
    can_respond = models.BooleanField(default=False)
    review_got_from = models.TextField(null=True)

    country = models.ForeignKey('api.Country', on_delete=models.CASCADE, null=True)
    city = models.ForeignKey('api.City', on_delete=models.CASCADE, null=True)
    tour = models.ForeignKey('api.Tour', on_delete=models.CASCADE, null=True)


class Agency(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    stream = models.PositiveSmallIntegerField(choices=STREAM_CHOICES)


class Country(models.Model):
    code = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

class City(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)

class Tour(models.Model):
    name = models.CharField(max_length=100)
    stream = models.PositiveSmallIntegerField(choices=STREAM_CHOICES)
    client = models.ForeignKey(User, on_delete=models.CASCADE)

class StreamNames(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(unique=True, upload_to='stream_images')

class Stream(models.Model):
    PENDING = 1
    CHECKING = 2
    WRONG = 3
    CORRECT = 4

    STATUS_CHOICES = (
        (PENDING, 'pending'),
        (CHECKING, 'checking'),
        (WRONG, 'wrong'),
        (CORRECT, 'correct'),)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_stream = models.CharField(max_length=50)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    attempts = models.IntegerField(default=0)

    class Meta:
        abstract = True

class UrlStream(Stream):
    product_name = models.CharField(max_length=500)
    url = models.CharField(max_length=1000)

class CredentialStream(Stream):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

class ApiKeyStream(Stream):
    page_id = models.CharField(max_length=50)
    api_key = models.CharField(max_length=1000)

class ScheduleEmailAddress(models.Model):
    name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    client = models.ForeignKey(User, on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.email

class ExportSchedule(models.Model):
    SEARCH_FACTOR = (
        (0, 'source_stream'),
        (1, 'keywords'),
        (2, 'country_code'),
        (3, 'tours'),
    )

    FORMAT = (
        (0, 'PDF'),
        (1, 'xlsx'),
        (2, 'xls'),
    )

    DATE_RANGE = (
        (0, 'Daily'),
        (1, 'Weekly'),
        (2, 'Montly'),
    )

    name = models.CharField(max_length=255, null=True)
    schedule = models.TextField(null=True)
    search_factor = models.PositiveSmallIntegerField(choices=SEARCH_FACTOR, null=True)
    format = models.PositiveSmallIntegerField(choices=FORMAT, null=True)
    # Date range in which the data should be populated (last day/week/month)
    date_range_export = models.PositiveSmallIntegerField(choices=DATE_RANGE, null=True)
    email_addresses = models.ManyToManyField(ScheduleEmailAddress)
    schedule_id = models.CharField(max_length=255, null=True)
    client = models.ForeignKey(User, on_delete=models.CASCADE,null=True)


class Notification(models.Model):
    SUCCESS = 1
    WARNING = 2
    DANGER = 3

    STATUS_CHOICES = [
        (SUCCESS, 'Success'),
        (WARNING, 'Warning'),
        (DANGER, 'Danger'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES,null=True)
    text = models.TextField()
    client_field = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notifications', null=True)
    datetime = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)



class Payment(models.Model):
    PAYED=0
    PENDING=1
    STATUS_CHOICES = [
        (PAYED, 'Payed'),
        (PENDING, 'Pending')
    ]

    payment_intent_id = models.CharField(max_length=255)
    subscription_id = models.CharField(max_length=255)
    company = models.ForeignKey('authentication.Company', on_delete=models.DO_NOTHING)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=PENDING)
    plan = models.PositiveSmallIntegerField(choices=settings.PLAN_CHOICES, default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment Intent ID: {self.payment_intent_id} | Company ID: {self.company.id}"

