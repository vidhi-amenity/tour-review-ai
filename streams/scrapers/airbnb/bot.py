from streams.scrapers.main_bot import Mainbot
from .utils import *
from api.models import Review, AIRBNB
from authentication.models import User
from django.conf import settings
from django.db import transaction

class ScraperBot(Mainbot):
    def __init__(self, obj, is_adding_datastream=False):
        self.link = obj.url + '&locale=en'
        print(self.link)
        # https://www.airbnb.com/experiences/3638200?location=Madrid&currentTab=experience_tab&federatedSearchId=b0e08e15-9cb0-402e-ab06-c27d5e609fee&searchId=67c1d4d4-de43-4fcf-b0b2-bbd52f100a7e&sectionId=36cc8f5f-6fb3-4766-bd23-a19ce1629fd4&_set_bev_on_new_domain=1679757817_NmQ3OWRiYmNiZWI5&enable_auto_translate=false&locale=en
        self.product = obj.product_name
        self.results = []
        self.zip_code = None
        self.address = None
        self.client = obj.user.created_by if obj.user.created_by else obj.user

        super().__init__(__file__)
        try:
            self.start()
            self.close(instance=obj, success=True, is_adding_datastream=is_adding_datastream)
        except:
            print("Something went wrong with Airbnb Scraper")
            self.close(instance=obj, success=False, is_adding_datastream=is_adding_datastream)


    def start(self):
        self.driver.get(self.link)
        # self.click_on_translate()
        self.show_reviews()
        self.scroll_down_into_modal()
        self.scrape()

    def click_on_translate(self):
        translate_modal = self.wait_for_el('translate_button')
        translate_modal.click()
        self.sleep(2)

    def scroll_down(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.sleep(2)

    def scroll_down_into_modal(self):
        self.sleep(10)
        # modal = self.wait_for_el('modal')
        # for x in range(1):
        #     self.driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', modal)
        #     self.sleep(3)

    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.sleep(2)
    def show_reviews(self):
        show_reviews = self.wait_for_el('show_reviews')
        show_reviews.click()
        self.sleep(2)

    def scrape(self):
        reviews = self.find_el('reviews', multiple=True)
        self.scroll_to_element(reviews[0])
        for item in reviews:
            try:
                self.scrape_item(item)
            except Exception as e:
                print(f'AIRBNB {e}')


    def scrape_item(self, item):
        self.scroll_to_element(item)
        review_text = self.find_el('review', item).text
        date = self.find_el('date', item).text
        product_id = item.get_attribute('data-review-id')
        responded = True if len(self.find_el('response', item, multiple=True)) else False
        img = self.find_el('img', item).get_attribute('src')

        review = Review.objects.filter(product_id=product_id, source_stream=AIRBNB).first()
        if not review:
            try:
                with transaction.atomic():
                    Review.objects.update_or_create(
                        date=clean_date(date),
                        product_id=product_id,
                        defaults={
                            "product": self.product,
                            "review_text": remove_emoji(review_text),
                            "responded": responded,
                            "source_stream": AIRBNB,
                            "review_url": "https://supplier.getyourguide.com/reviews",
                            "img": img,
                            "client": self.client  # the User is used here
                        }
                    )
            except Exception as e:
                print("Failed to save the review due to error: ", e)
