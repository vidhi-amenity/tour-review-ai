from streams.scrapers.main_bot import Mainbot
from selenium.webdriver.common.keys import Keys
import datetime
from .utils import *
from api.models import Review, TRIPADVISOR
from django.conf import settings
from django.db import transaction


class ScraperBot(Mainbot):
    def __init__(self, obj, is_adding_datastream=False):
        self.link = replace_domain_extension(obj.url)
        self.product = obj.product_name
        self.is_adding_datastream = is_adding_datastream
        self.results = []
        self.zip_code = None
        self.address = None
        self.reviews_fetched = False
        self.client = obj.user.created_by if obj.user.created_by else obj.user
        super().__init__(__file__)

        try:
            self.start()
            self.close(instance=obj, success=True, is_adding_datastream=is_adding_datastream)
        except Exception as e:
            print("Boat Error: "  + e)
            print("Something went wrong with Tripadvisor Scraper")
            if self.reviews_fetched:
                self.close(instance=obj, success=True, is_adding_datastream=is_adding_datastream)
            else:
                self.close(instance=obj, success=False, is_adding_datastream=is_adding_datastream)

    def start(self):
        self.driver.get(self.link)
        self.sleep(5)
        accept_button = self.wait_for_el('onetrust-accept')
        # accept_button = self.driver.find_element('id', "onetrust-accept-btn-handler")
        accept_button.click()
        self.sleep(1)

        # Loop to keep scraping and clicking the "Next" button
        idx = 0
        while True:
            if self.is_adding_datastream and idx >= 1:
                break
            if idx >= 3:
                break
            self.scroll_down()
            self.scrape()
            can_continue = self.click_next()
            idx += 1
            if not can_continue:
                break

    def scroll_to_element(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.sleep(2)

    def scroll_down(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        self.sleep(1)

    def click_next(self):
        try:
            self.sleep(1)
            next_button = self.driver.find_element('class name', "xkSty")
            next_button.click()
            self.sleep(3)
            return True
        except Exception as e:
            print("Reached the last page or an error occurred.")
            return False

    def get_rating(self, review_tab):
        try:
            rating_svg = review_tab.find_element('css selector',
                                                 ' div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > svg:nth-child(1)')
            rating = rating_svg.get_attribute('aria-label')
            return rating
        except Exception as e:
            rating_svg = review_tab.find_element('css selector', 'div > div > div:nth-child(2) > svg')
            rating = rating_svg.get_attribute('aria-label')
            return rating

    def scrape(self):

        self.sleep(5)
        reviews = self.find_el('reviews', multiple=True)

        last_review_elem = None
        for review_tab in reviews:
            self.scroll_to_element(review_tab)
            try:
                review_elements = review_tab.find_elements('class name', 'yCeTE')
                if len(review_elements) > 1:
                    review = review_elements[1].text
                    last_review_elem = review_tab
                    name = review_tab.find_elements('tag name', 'a')[1].text
                    img_url = review_tab.find_element('tag name', 'picture').find_element('tag name', 'img').get_attribute("src")
                    rating = self.get_rating(review_tab)
                    date = review_tab.find_element('xpath',
                                                   './/div[contains(@class, "TreSq")]/div[contains(@class, "biGQs _P pZUbB ncFvv osNWb")]').text
                    product_id = generate_id(date + review)
                    print(clean_date(date))
                    Review.objects.update_or_create(
                        date=clean_date(date),
                        product_id=product_id,
                        defaults={
                            "product": self.product,
                            "rating": clean_rating(rating),
                            "review_text": remove_emoji(review),
                            "responded": True if review_tab.find_elements('css selector', '.hjJJO.PJ') else False,
                            "source_stream": TRIPADVISOR,
                            "review_url": self.link,
                            "img": img_url,
                            "client": self.client
                        })
                    print('Review Processed')
                    self.reviews_fetched = True
                else:
                    self.scroll_to_element(last_review_elem)
                    continue
            except Exception as e:
                print(f"Error while processing a review: {e}")
                continue