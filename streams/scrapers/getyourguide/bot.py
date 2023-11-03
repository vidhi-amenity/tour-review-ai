from streams.scrapers.main_bot import Mainbot
from selenium.webdriver.common.keys import Keys
import datetime
from .utils import *
from api.models import Review, GETYOURGUIDE
from django.conf import settings
from django.db import transaction


class ScraperBot(Mainbot):
    def __init__(self, obj, is_adding_datastream=False):
        today = datetime.date.today()
        seven_days_ago = today - datetime.timedelta(days=1)
        self.zip_code = None
        self.address = None
        self.login_link = f'https://supplier.getyourguide.com/reviews#orderType=desc&page=1&reviewDateFrom={seven_days_ago.strftime("%Y-%m-%d")}'
        self.username = obj.username
        self.password = obj.password
        self.pages = []
        self.results = []
        self.client = obj.user.created_by if obj.user.created_by else obj.user

        super().__init__(__file__)

        try:
            self.start()
            self.close(instance=obj, success=True, is_adding_datastream=is_adding_datastream)
        except:
            print("Something went wrong with Getyourguide Scraper")
            self.close(instance=obj, success=False, is_adding_datastream=is_adding_datastream)

    def start(self):
        self.driver.get(self.login_link)
        self.login()
        self.sleep(15)
        self.get_pages()


    def login(self):
        field_username = self.wait_for_el('username_field')
        field_username.send_keys(self.username)

        field_password = self.wait_for_el('password_field')
        field_password.send_keys(self.password)
        self.sleep(2)
        field_password.send_keys(Keys.ENTER)

    def get_pages(self):
        self.scroll_down()
        self.scrape_products()
        # while True:
        #     self.scroll_down()
        #     self.scrape_products()
        #     try:
        #         button = self.find_el('next-page')
        #         button.click()
        #         self.sleep(5)
        #     except Exception as e:
        #         print('Page ')
        #         print(e)
        #         break

    def scroll_down(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.sleep(2)

    def scrape_products(self):
        items = self.find_el('reviews',multiple=True)
        for item in items:
            review = ''
            try:
                review = self.find_el('review',item).text
            except:
                pass
            element = self.find_el('date',item).text.split(',')[1] + ' ' + self.find_el('date',item).text.split(',')[2]
            date = element.split('|')[0].split('by')[0]
            product = element.split('|')[2]
            rating = len(item.find_elements('class name', 'star-rating__icon--full'))
            id = self.find_el('id', item, multiple=True)[1].get_attribute('innerHTML')
            img = self.find_el('tour-thumbnail', item).get_attribute('src')

            responded = False
            try:
                with transaction.atomic():
                    Review.objects.update_or_create(
                        date=clean_date(date),
                        product_id=clean_id(id),
                        defaults={
                            "product": product,
                            "rating": int(rating/2),
                            "review_text": review,
                            "responded": responded,
                            "source_stream": GETYOURGUIDE,
                            "review_url": "https://supplier.getyourguide.com/reviews",
                            "img": img,
                            "client": self.client
                        }
                    )
            except Exception as e:
                print('failed to save due to: ', e)
