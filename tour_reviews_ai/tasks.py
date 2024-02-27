from __future__ import absolute_import, unicode_literals
from celery import shared_task
import json
from streams.scrapers.utilities import import_bot
import openai
from django.conf import settings
from streams.apis.facebook_apis import get_facebook_reviews, get_facebook_comments, get_instagram_comments
from api.models import Review, Country, Tour, ExportSchedule, City, CredentialStream, Stream, ApiKeyStream
import pycountry
from api.utilities.export_report import export_pdf, export_xlsx
from api.utilities.send_email import send
from datetime import timedelta, date
import tempfile
import os
from django.shortcuts import get_object_or_404
from api.utils import get_streams
from api.utils import create_notification
from api.serializers import failure_message, success_message
from api.models import UrlStream, CredentialStream, ApiKeyStream, \
    CIVITAS, GETYOURGUIDE, AIRBNB, VIATOR, \
    TRIPADVISOR, KLOOK, EXPEDIA, INSTAGRAM, \
    FACEBOOK, GOOGLE
from django.utils import timezone


@shared_task
def run_background_scrapers():
    print("Scrapper is started......!")
    now = timezone.now()
    urls = CredentialStream.objects.filter(user__related_users__subscription_ends__gt=now, source_stream=CIVITAS)
    for url in urls:
        try:
            scrape.delay(url.id, 'CredentialStream')
        except Exception as e:
            print(e)

    urls = CredentialStream.objects.filter(user__related_users__subscription_ends__gt=now, source_stream=GETYOURGUIDE)
    for url in urls:
        try:
            scrape.delay(url.id, 'CredentialStream')
        except Exception as e:
            print(e)

    urls = UrlStream.objects.filter(user__related_users__subscription_ends__gt=now, source_stream=AIRBNB)
    for url in urls:
        try:
            scrape.delay(url.id, 'UrlStream')
        except Exception as e:
            print(e)

    urls = UrlStream.objects.filter(user__related_users__subscription_ends__gt=now, source_stream=VIATOR)
    for url in urls:
        try:
            scrape.delay(url.id, 'UrlStream')
        except Exception as e:
            print(e)

    urls = UrlStream.objects.filter(user__related_users__subscription_ends__gt=now, source_stream=TRIPADVISOR)
    for url in urls:
        try:
            scrape.delay(url.id, 'UrlStream')
        except Exception as e:
            print(e)

    urls = CredentialStream.objects.filter(user__related_users__subscription_ends__gt=now, source_stream=KLOOK)
    for url in urls:
        try:
            scrape.delay(url.id, 'CredentialStream')
        except Exception as e:
            print(e)

    urls = UrlStream.objects.filter(user__related_users__subscription_ends__gt=now, source_stream=EXPEDIA)
    for url in urls:
        try:
            scrape.delay(url.id, 'UrlStream')
        except Exception as e:
            print(e)

    urls = ApiKeyStream.objects.filter(user__related_users__subscription_ends__gt=now, source_stream=FACEBOOK)
    for url in urls:
        try:
            obj = get_object_or_404(ApiKeyStream, id=url.id)
            res = get_facebook_reviews(obj)
            get_facebook_comments(obj)
            success = res['success']
            client = obj.user.created_by if obj.user.created_by else obj.user
            text = f' ApiKey with page_id = "{obj.api_key}" is expired, please update it with a new ' \
                   'ApiKey to be able to keep fetching the reviews'
            if not success:
                obj.status = Stream.WRONG
                create_notification(client, status=failure_message['status'], text=text, source_stream=obj.source_stream)
            obj.save()

        except Exception as e:
            print(e)

    urls = ApiKeyStream.objects.filter(user__related_users__subscription_ends__gt=now, source_stream=INSTAGRAM)
    for url in urls:
        try:
            obj = get_object_or_404(ApiKeyStream, id=url.id)
            res = get_instagram_comments(obj)
            success = res['success']
            client = obj.user.created_by if obj.user.created_by else obj.user
            text = f' ApiKey with page_id = "{obj.api_key}" is expired, please update it with a new ' \
                   'ApiKey to be able to keep fetching the reviews'
            if not success:
                obj.status = Stream.WRONG
                create_notification(client, status=failure_message['status'], text=text, source_stream=obj.source_stream)
            obj.save()

        except Exception as e:
            print(e)

    analise_reviews()

@shared_task
def task_analise_reviews():
    try:
        analise_reviews()
    except Exception as e:
        print(e)


@shared_task
def analise_reviews(*args, **kwargs):
    # https: // platform.openai.com / playground?model = text - davinci - 003
    # from tour_reviews_ai.tasks import analise_reviews
    # analise_reviews()

    reviews = Review.objects.filter(ai_checked=False)

    for review in reviews:
        city = None
        country_instance = None
        try:
            if not review.review_text:
                review.ai_checked = True
                review.sentiment = 2
                review.save()
                continue

            openai.api_key = settings.OPENAI_API_KEY
            response = openai.Completion.create(
                engine='text-davinci-003',
                prompt=create_prompt(review.product, review.review_text),
                temperature=0.75,
                max_tokens=256
            )

            print(response.choices[0].text)
            score_json = json.loads(response.choices[0].text.strip())  # Remove leading/trailing white space and newlines
            print(score_json)
            review.ai_checked = True
            review.sentiment = score_json['sentiment']
            if review.rating == 0:
                review.rating = score_json['rating']
            review.places = json.dumps(score_json['places'])
            review.country_code = score_json['country_code']
            city = score_json['city']
            review.save()
        except Exception as e:
            print(e)
            review.ai_checked = True
            review.sentiment = 2
            if review.rating == 0:
                review.rating = 2.5
            review.save()

        country_instance = Country.objects.filter(code=review.country_code).first()
        if not country_instance:
            try:
                country = pycountry.countries.get(alpha_2=review.country_code)
                country_name = country.name
                country_instance = Country.objects.create(
                    code=review.country_code,
                    name=country_name
                )
            except Exception as e:
                print("Country not found")

        review.country = country_instance

        if city:
            try:
                city_instance = City.objects.filter(name=city).first()
                if not city_instance:
                    city_instance = City.objects.create(
                        country=country_instance if country_instance else None,
                        name=city
                    )
                elif city_instance and country_instance:
                    city_instance.country = country_instance
                    city_instance.save()

                review.city = city_instance
            except Exception as e:
                print(e)
                print("City not found")

        if review.product:
            tour = Tour.objects.filter(
                name=review.product,
                stream=review.source_stream,
                client=review.client
            ).first()
            if not tour:
                tour = Tour.objects.create(
                    name=review.product,
                    stream=review.source_stream,
                    client=review.client,
                )
            review.tour = tour

        review.save()




def create_prompt(product, review):
    return """
    
    INSTRUCTIONS:
    Please rate the sentiment of the following text (1-3), the rating (1-5), provide a list of restaurants/locations mentioned in the REVIEW and extract the country code and the city from the PRODUCT.
    
    Respond with this json:
    {
        "sentiment": 3,
        "rating": 5,
        "country_code": "",
        "city": "",
        "places": [
            {
                "name": "",
                "type": "restaurant"
            },
            {
                "name": "",
                "type": "location"
            }
        ]
    }
    
    PRODUCT:
    %s
    
    REVIEW:
    %s
    """ % (product, review)


@shared_task
def task_schedule_email_report(export_schedule_id, by_rating, by_agency, by_tour, by_country, by_responded):
    try:
        export_schedule = ExportSchedule.objects.get(id=export_schedule_id)
        end_date = date.today() - timedelta(days=1)
        print("END DATE = ", end_date)

        if export_schedule.date_range_export == 0:
            subject = 'Tour Review Daily Report'
            start_date = date.today() - timedelta(days=2)
        elif export_schedule.date_range_export == 1:
            subject = 'Tour Review Weekly Report'
            start_date = date.today() - timedelta(days=8)
        elif export_schedule.date_range_export == 2:
            subject = 'Tour Review Monthly Report'
            start_date = date.today() - timedelta(days=32)
        
        print("START DATE = ", start_date)

        search_factor = get_text_from_id(export_schedule.search_factor)
        print("SEARCH FACTOR = ", search_factor)

        email_addresses = [e.email for e in export_schedule.email_addresses.all()]
        print("EMAIL = ", email_addresses)

        if export_schedule.format == 0:
            pdf_data, title = export_pdf(by_rating, by_agency, by_tour, by_country, by_responded, start_date, end_date, search_factor)
            new_file_path = save_tmp_file(pdf_data, 'pdf')

        elif export_schedule.format == 1:
            xlsx_data, title, extension = export_xlsx(by_rating, by_agency, by_tour, by_country, by_responded, start_date, end_date, search_factor)
            xlsx_data = xlsx_data.getvalue()
            new_file_path = save_tmp_file(xlsx_data, extension)

        elif export_schedule.format == 2:
            xlsx_data, title, extension = export_xlsx(by_rating, by_agency, by_tour, by_country, by_responded, start_date, end_date, search_factor, xls=True)
            xlsx_data = xlsx_data.getvalue()
            new_file_path = save_tmp_file(xlsx_data, extension)

        email = send(subject, f'Export of {title}', email_addresses, new_file_path)
        return email
    except Exception as e:
        print(e)


def get_text_from_id(search_id):
    for item in ExportSchedule.SEARCH_FACTOR:
        if item[0] == search_id:
            return item[1]
    return None


def save_tmp_file(doc_data, suffix):
    with tempfile.NamedTemporaryFile(suffix=f'.{suffix}', delete=False) as temp_file:
        temp_file.write(doc_data)
        temp_file_path = temp_file.name

    file_name = f"review_report.{suffix}"
    new_file_path = os.path.join(os.path.dirname(temp_file_path), file_name)
    os.rename(temp_file_path, new_file_path)
    return new_file_path


def save_tmp_file_xlsx(doc_data, suffix):
    with tempfile.NamedTemporaryFile(suffix=f'.{suffix}', delete=False) as temp_file:
        temp_file.write(doc_data.getvalue())  # Use getvalue() to read binary data from BytesIO
        temp_file_path = temp_file.name

    file_name = f"review_report.{suffix}"
    new_file_path = os.path.join(os.path.dirname(temp_file_path), file_name)
    os.rename(temp_file_path, new_file_path)
    return new_file_path

@shared_task(name="scrape")
def scrape(instance_id, type, is_adding_datastream=False, *args, **kwargs):
    print("Scrape Type = ", type)
    if type == 'UrlStream':
        instance = get_object_or_404(UrlStream, id=instance_id)
    if type == 'CredentialStream':
        instance = get_object_or_404(CredentialStream, id=instance_id)

    if is_adding_datastream:
        instance.status = Stream.CHECKING
    instance.save()

    stream_name = get_streams(instance.source_stream)
    Bot = import_bot(stream_name)
    bot = Bot(instance, is_adding_datastream)
    print("BOT = ", bot)
    if not settings.PRODUCTION:
        return bot

