from streams.scrapers.main_bot import Mainbot
from selenium.webdriver.common.keys import Keys
import datetime
from .utils import *
from api.models import Review, KLOOK
from django.conf import settings
import random
from django.db import transaction


class ScraperBot(Mainbot):
    def __init__(self, obj, is_adding_datastream=False):
        self.zip_code = None
        self.address = None
        self.link = 'https://merchant.klook.com/reviews'
        self.username = obj.username
        self.password = obj.password
        self.results = []
        self.client = obj.user.created_by if obj.user.created_by else obj.user

        super().__init__(__file__)

        try:
            self.start()
            self.close(instance=obj, success=True, is_adding_datastream=is_adding_datastream)
        except:
            print("Something went wrong with Klook Scraper")
            self.close(instance=obj, success=False, is_adding_datastream=is_adding_datastream)

    def start(self):
        self.driver.get(self.link)
        self.random_sleep(0.5, 1)
        self.random_sleep(0.5, 1)
        self.login()
        self.switch_to_frame()
        self.scroll_down()
        self.scrape()

    def random_sleep(self, from_, to):
        duration = random.uniform(from_, to)
        self.sleep(duration)

    def login(self):
        email = self.find_el('email')
        email.send_keys(self.username)
        self.random_sleep(2, 4)
        self.random_sleep(2, 4)
        password = self.find_el('password')
        password.send_keys(self.password)
        self.random_sleep(2, 4)
        self.random_sleep(2, 4)
        signin = self.find_el('login_button')
        signin.click()
        self.sleep(5)

    def switch_to_frame(self):
        frame_element = self.wait_for_el('iframe')
        self.driver.switch_to.frame(frame_element)

    def scroll_down(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.sleep(1)


    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.sleep(2)

    def scrape(self):
        reviews = self.wait_for_el('reviews',multiple=True)
        for review in reviews:
            try:
                self.scroll_to_element(review)
                product_id = self.find_el('product_id', item=review).text
                product = self.find_el('product', item=review).text
                date = self.find_el('date', item=review).text
                review_text = self.find_el('review', item=review).text
                rating_style = self.driver.find_element('class name', 'klk_rate_light').get_attribute('style')

                rating = 1
                if rating_style == 'width: 75px;':
                    rating = 5
                elif rating_style == 'width: 60px;':
                    rating = 4
                elif rating_style == 'width: 45px;':
                    rating = 3
                elif rating_style == 'width: 30px;':
                    rating = 2
                elif rating_style == 'width: 15px;':
                    rating = 1

                responded = True if (self.find_el('response', item=review).text) else False
                try:
                    with transaction.atomic():
                        Review.objects.update_or_create(
                            date=clean_date(date),
                            product_id=product_id,
                            defaults={
                                "product": product,
                                "rating": rating,
                                "review_text": review_text,
                                "responded": responded,
                                "source_stream": KLOOK,
                                "review_url": "https://merchant.klook.com/reviews",
                                "img": None,
                                "client": self.client
                            }
                        )
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
