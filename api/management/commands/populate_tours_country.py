from django.core.management.base import BaseCommand
from api.models import Review, Country, Tour
import pycountry


class Command(BaseCommand):
    help = 'Copy or modify Products from ScrapingCategoryResultDetail'

    def handle(self, *args, **options):
        # Gets all promos in the data downloaded
        reviews = Review.objects.all()

        for r in reviews:
            country = Country.objects.filter(code=r.country_code).exists()
            if not country:
                try:
                    country = pycountry.countries.get(alpha_2=r.country_code)
                    country_name = country.name
                    Country.objects.create(
                        code=r.country_code,
                        name=country_name
                    )
                except:
                    print("Country not found")

            if r.product:
                tour = Tour.objects.filter(name=r.product, client=r.client, stream=r.source_stream).exists()
                if not tour:
                    Tour.objects.create(
                        name=r.product,
                        stream=r.source_stream,
                        client=r.client
                    )
