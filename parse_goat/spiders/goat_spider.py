import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time


class GoatSpider(scrapy.Spider):
    name = "goat_spider"
    allowed_domains = ["goat.com"]
    start_urls = ["https://www.goat.com/sneakers"]

    def __init__(self, *args, **kwargs):
        super(GoatSpider, self).__init__(*args, **kwargs)

        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.parse,
            meta={'driver': self.driver}
        )

    def parse(self, response):
        driver = response.meta.get('driver')

        if driver is None:
            self.logger.error("Driver not found in response.meta")
            return

        driver.get(self.start_urls[0])

        time.sleep(10)

        try:
            accept_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept all cookies')]")
            accept_button.click()
            time.sleep(2)
        except Exception as e:
            self.logger.warning("Accept cookies button not found or could not be clicked.")
            self.logger.warning(e)

        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(10)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        products = driver.find_elements(By.CSS_SELECTOR, "div[data-qa='grid_cell_product']")

        for product in products:
            link = product.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            yield {
                "sneaker_link": link
            }

    def closed(self, reason):
        self.driver.quit()