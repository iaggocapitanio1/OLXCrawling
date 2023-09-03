import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from olx.utils import get_page_number_from_url, get_error_path
from selenium.webdriver.remote.webelement import WebElement
from olx.items import OlxItem
from olx import settings

class OlxSpider(scrapy.Spider):
    """
    This spider uses Playwright to scroll the page and make all the items visible
    """
    name = "olx"
    allowed_domains = ["olx.com.br"]
    ITEMS_XPATH = '//div[@id="main-content"]//div[contains(@class, "sc-bb3a36b6-0") and contains(@class, "bPPSiI")]'
    PRICE_XPATH = './/section/div[2]/div[1]/div[2]/h3'
    TITLE_XPATH = './/section/div[2]/div[1]/div[1]/a/h2'
    LINK_XPATH = './/section/div[2]/div[1]/div[1]/a'
    DETAIL_XPATH = '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[9]/div/div/div/div[2]/div/p/span/text()'
    start_urls = ["https://olx.com.br/imoveis/estado-sc"]

    MAX_TIMEOUT = 15

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = webdriver.ChromeOptions()
        for arg in kwargs.get('options', []):
            options.add_argument(arg)
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=options)
        self.actions = ActionChains(self.driver)
        self.page_threshold = int(kwargs.get('page_threshold', settings.PAGE_THRESHOLD ))

    @property
    def page_threshold(self) -> int:
        return self._page_threshold

    @page_threshold.setter
    def page_threshold(self, value: int):
        self._page_threshold = value

    def parse_title(self, item: WebElement, wait=None) -> str:
        return self._parse_element(item, wait, xpath=self.TITLE_XPATH)

    def parse_price(self, item: WebElement, wait=None) -> str:
        return self._parse_element(item, wait, xpath=self.PRICE_XPATH)

    def parse_link(self, item: WebElement, wait=None) -> str:
        return self._parse_element(item, wait, xpath=self.LINK_XPATH, tag_attr='href')

    def parse_item_detail(self, response: Response, **kwargs) -> str:
        title = response.meta.get('title', 'Not found')
        price = response.meta.get('price', 'Not found')
        description = response.xpath(self.DETAIL_XPATH).get()
        yield OlxItem(description=description, title=title, price=price)

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.error_call_back)

    @staticmethod
    async def error_call_back(failure):
        """
        This method is called when an error occurs.
        :param failure:
        :return:
        """
        error_path = get_error_path(failure)
        page = failure.request.meta['playwright_page']
        await page.screenshot(path=error_path)
        await page.close()
        print(f"Error: {failure}")

    def parse(self, response: Response, **kwargs) -> None:
        """
        Parse the response and yield the items.
        :param response:
        :param kwargs:
        :return:
        """
        self.driver.get(response.url)
        wait = WebDriverWait(self.driver, self.MAX_TIMEOUT)
        items = self.driver.find_elements(By.XPATH, self.ITEMS_XPATH)

        for item in items[2:]:
            self.actions.move_to_element(item).perform()
            try:
                price = self.parse_price(item, wait)
                title = self.parse_title(item, wait)
                link = self.parse_link(item, wait)

                yield response.follow(url=link,
                                      callback=self.parse_item_detail,
                                      errback=self.error_call_back,
                                      meta={'title': title, 'price': price}
                                      )

            except TimeoutException:
                print("Timed out waiting for elements to become visible or couldn't find them for this item.")

        next_page_url = self.get_next_page_url(response)
        if next_page_url:
            yield response.follow(url=next_page_url, callback=self.parse)

    def get_next_page_url(self, response: Response) -> str | None:
        """
        Get the next page url, it must respect a threshold of pages to be scraped.
        :param response: The Scrapy Response object.
        :return: It can return a string or None, if it returns None, it means that the threshold was reached or there is
        no more content to be scraped.
        """
        content = response.xpath(self.ITEMS_XPATH)
        url = response.url
        number: int = get_page_number_from_url(url)

        if not content or number > self.page_threshold:
            return None

        if number == 0:
            return f"{url}?o=2"

        return url.replace(f'o={number}', f'o={number + 1}')

    def closed(self, reason):
        """
        This method is called when the spider is closed.
        :param reason:
        :return:
        """
        self.driver.quit()

    def _parse_element(self, item: WebElement, wait: WebDriverWait | None = None, **kwargs) -> str:
        """
        Parse an element from the item, a general method to be used by other methods to parse elements.
        :param item: A WebElement object
        :param wait: A WebDriverWait object
        :param kwargs: It can accept the following arguments: xpath, error_msg, tag
        :return: it can return  the text of the element or the error_msg
        """
        xpath = kwargs.get('xpath')
        error_msg: str = kwargs.get('error_msg', "Element Not Found")
        tag_attr = kwargs.get('tag_attr', 'innerText')

        if not wait:
            wait = WebDriverWait(self.driver, self.MAX_TIMEOUT)
        try:
            element: WebElement = wait.until(EC.visibility_of(item.find_element(By.XPATH, xpath)))
            return element.get_attribute(tag_attr) if element else error_msg
        except TimeoutException:
            print("Timed out waiting for elements to become visible or couldn't find them for this item.")
            return error_msg
