from streams.scrapers.main_bot import Mainbot
from .utils import *
from selenium.webdriver.common.keys import Keys
from django.conf import settings
from api.models import Review, CIVITAS
from django.db import transaction


class ScraperBot(Mainbot):
    def __init__(self, obj, is_adding_datastream=False):
        self.zip_code = None
        self.address = None
        self.login_link = 'https://www.civitatis.com/es/proveedores/'
        self.username = obj.username
        self.password = obj.password
        self.client = obj.user.created_by if obj.user.created_by else obj.user

        self.pages = []
        self.results = []
        print(self.client)
        super().__init__(__file__)
        try:
            self.start()
            self.close(instance=obj, success=True, is_adding_datastream=is_adding_datastream)
        except:
            print("Something went wrong with Civitatis Scraper")
            self.close(instance=obj, success=False, is_adding_datastream=is_adding_datastream)

    def start(self):
        self.driver.get(self.login_link)
        # self.accept_cookies()
        self.login()
        self.check_logged()
        self.scroll_down()
        self.get_pages()
        self.scrape_products()

    def accept_cookies(self):
        button = self.wait_for_el('button_accept_cookies')
        button.click()
        self.sleep(2)

    def login(self):
        button_insert_credentials = self.wait_for_el('button_insert_credential')
        button_insert_credentials.click()

        field_username = self.wait_for_el('username_field')
        field_username.send_keys(self.username)

        field_password = self.wait_for_el('password_field')
        field_password.send_keys(self.password)
        self.sleep(2)
        field_password.send_keys(Keys.ENTER)


    def check_logged(self):
        self.wait_for_el('sidebar')
        "https://www.civitatis.com/es/proveedores/v2/opiniones/?timePeriodType=today"
        # self.wait_for_el('filter').click()
        # self.wait_for_el('select_today').click()
        # self.wait_for_el('sort_table').click()

    def get_pages(self):
        self.pages = self.wait_for_el('pagination')\
            .find_element('tag name', 'span')\
            .find_elements('class name', 'paginate_button')
        print(self.pages)
        print(len(self.pages))

    def scroll_down(self):
        for _ in range(2):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.sleep(1)

    def scrape_products(self):
        # Collect all review waiting for a reply
        try:
            waiting_reply = self.wait_for_el('waiting_reply_table')
            all_waiting_reply = waiting_reply.find_elements('tag name', 'tr')
            for r in all_waiting_reply[1:]:
                self.create_review_object(r, to_respond=True)
        except Exception as e:
            print(e)

        for p, pg in enumerate(self.pages):
            if p >= 3:
                break
            # Collect all review with no reply
            replied = self.wait_for_el('not_reply_table')
            all_replied = replied.find_elements('tag name', 'tr')
            for r in all_replied[1:]:
                self.create_review_object(r)
            self.get_pages()
            if p == len(self.pages)-1:
                break
            self.pages[p+1].click()

        print(self.results)

    def create_review_object(self, review, to_respond=False):
        fields = review.find_elements('tag name', 'td')
        responded = fields[5].find_elements('tag name', 'i')
        responded = True if responded else False
        if to_respond:
            responded = False
        try:
            with transaction.atomic():
                Review.objects.update_or_create(
                    date=clean_date(fields[1].text),
                    product_id=fields[0].text,
                    defaults={
                        "product": fields[2].text,
                        "rating": int(fields[3].text)/2,
                        "review_text": fields[4].find_element('tag name', 'span').text,
                        "responded": responded,
                        "source_stream": CIVITAS,
                        "review_url": "https://www.civitatis.com/es/proveedores/v2/opiniones",
                        "client": self.client
                    }
                )


        except Exception as e:
            print(e)
            print('Error creating review object')

