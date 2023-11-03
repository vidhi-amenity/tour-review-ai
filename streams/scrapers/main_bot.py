from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
import os
import json
from django.conf import settings
from api.utils import create_notification
from api.models import Stream
from api.serializers import failure_message, success_message
from streams.models import Proxy
from tour_reviews_ai.tasks import scrape

SCROLL_INTERVAL = 2.5
NORMAL_SLEEP = 3


class Mainbot:

    def __init__(self, file_paths):
        self.SCROLL_INTERVAL = 2.5
        self.NORMAL_SLEEP = 3
        self.DRIVER_WAIT = 20
        self.CATEGORY = ""
        self.SUBCATEGORY1 = ""
        self.SUBCATEGORY2 = ""
        self.NO_VALUE = ""
        self.total_items = 0
        self.total_scraped_items = 0
        self.paths = self.get_paths(file_paths)
        self.destroy = False
        self.proxy = None
        self.driver = self.setProxyFromDispatcherWithAuth()

    def close(self, instance, success, is_adding_datastream=False):
        try:
            self.driver.quit()
        except:
            pass

        if self.proxy:
            self.proxy.in_use = False
            self.proxy.save()

        if is_adding_datastream:
            client = instance.user.created_by if instance.user.created_by else instance.user
            instance.attempts += 1
            if success:
                instance.status = Stream.CORRECT
                create_notification(client, status=success_message['status'], text=success_message['text'], source_stream=instance.source_stream)
            else:
                if instance.attempts <= 3:
                    _type = type(instance).__doc__.split('(')[0]
                    scrape.apply_async(args=[instance.id, _type, is_adding_datastream])
                else:
                    instance.status = Stream.WRONG
                    create_notification(client, status=failure_message['status'], text=failure_message['text'],
                                        source_stream=instance.source_stream)
            instance.save()

    def extract_el(self, e):
        return self.paths[e]['t'], self.paths[e]['v']

    def wait_for_el(self, el, time_to_wait=30, multiple=False, item=None):
        self.sleep(1)
        wait = WebDriverWait(self.driver, time_to_wait)
        if item:
            wait = WebDriverWait(item, time_to_wait)
        if multiple:
            return wait.until(EC.visibility_of_all_elements_located((self.extract_el(el))))
        return wait.until(EC.visibility_of_element_located((self.extract_el(el))))

    def find_el(self, el, item=None, multiple=False):
        method, value = self.extract_el(el)
        driver = item if item else self.driver
        if multiple:
            return driver.find_elements(method, value)
        return driver.find_element(method, value)

    def sleep(self, seconds):
        sleep(seconds)

    def get_paths(self, file_paths):
        # get the path of the paths.json file relative to the current file
        current_directory = os.path.dirname(os.path.abspath(file_paths))
        json_file_path = os.path.join(current_directory, 'paths.json')
        with open(json_file_path) as f:
            return json.load(f)


    def getOptions(self):
        options = Options()

        options.add_argument('window-size=1920x1080')
        if settings.PRODUCTION:
            options.add_argument("--headless=new")  # https://www.selenium.dev/blog/2023/headless-is-going-away/
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-dev-shm-usage") # Not used on kerberos

        # Disable css and images
        prefs = {"profile.managed_default_content_settings.images": 2,
                 "profile.managed_default_content_settings.stylesheets": 2}
        # options.add_experimental_option("prefs", prefs)

        return options


    def get_proxy(self):
        proxy = Proxy.objects.filter(in_use=False).first()
        if proxy:
            proxy.in_use = True
            # proxy.save()
            return proxy
        else:
            self.destroy = True


    def setProxyFromDispatcherWithAuth(self, ):
        options = self.getOptions()

        # if self.use_rotating_proxy:
        #     # Checks if there are any rotating proxy available, otherwise,
        #     # it destroys the current scraper and delay its execution
        #     self.proxy = self.get_proxy()
        #     if self.destroy:
        #         return None
        #     options.add_argument(f'--proxy-server=http://{self.proxy.endpoint}:{self.proxy.port}')
        #     self.proxy_used = f'http://{self.proxy.endpoint}:{self.proxy.port}'
        # else:
        #     # Checks if a session of the same selling point is already in execution,
        #     # otherwise, it destroys the current scraper and delay its execution
        #     self.get_current_scraper_session()
        #     if self.destroy:
        #         return None
        #
        #     # Proxies from https://proxy-seller.com/
        #     proxy_address = K_Dispatcher.retrieveWorkingProxyWithAuth(K_Dispatcher.checkMethod.Requests)
        #     proxy_address_components = self.extractProxyComponents(proxy_address)
        #     username = proxy_address_components['username']
        #     password = proxy_address_components['password']
        #     endpoint = proxy_address_components['endpoint']
        #     port = proxy_address_components['port']
        #     proxies_extension = proxies(username, password, endpoint, port)
        #     options.add_extension(proxies_extension)
        #     self.proxy_used = f'http://{username}:{password}@{endpoint}:{port}'

        # TODO Test rotatating proxy before uncommenting
        self.proxy = self.get_proxy()
        if self.destroy:
            return None
        options.add_argument(f'--proxy-server=http://{self.proxy.endpoint}:{self.proxy.port}')

        capabilities = webdriver.DesiredCapabilities.CHROME
        if settings.PRODUCTION:
            url = f'http://{settings.SELENIUM_GRID_HOST}:4444/wd/hub'
            driver = webdriver.Remote(
                command_executor=url,
                options=options,
                desired_capabilities=capabilities
            )
            driver.set_window_size(1920, 1080)
            return driver
        else:
            # options.add_argument("--headless=new")
            # # webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)  # used before selenium grid
            #
            # url = f'http://{settings.SELENIUM_GRID_HOST}:4444/wd/hub'
            # driver = webdriver.Remote(
            #     command_executor=url,
            #     options=options,
            #     desired_capabilities=capabilities
            # )
            # driver.set_window_size(1920, 1080)
            # return driver

            from selenium.webdriver.firefox.service import Service
            from webdriver_manager.firefox import GeckoDriverManager
            options = webdriver.FirefoxOptions()
            ## options.add_argument('--headless')
            return webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)

            return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
