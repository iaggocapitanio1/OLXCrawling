from typing import List

import scrapy
from scrapy.http import Response
from scrapy.selector import Selector

from olx.items import OlxItem
from olx.utils import get_page_number_from_url


class OlxSpider(scrapy.Spider):
    name = "olx"
    allowed_domains = ["olx.com.br"]
    ITEMS_XPATH = '//div[@id="main-content"]//div[contains(@class, "sc-bb3a36b6-0") and contains(@class, "bPPSiI")]'
    PRICE_XPATH = './/section/div[2]/div[1]/div[2]/h3'
    TITLE_XPATH = './/section/div[2]/div[1]/div[1]/a/h2'
    LINK_XPATH = './/section/div[2]/div[1]/div[1]/a'
    DETAIL_XPATH = '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[9]/div/div/div/div[2]/div/p/span'
    start_urls = ["https://olx.com.br/imoveis/estado-sc"]
    PAGE_THRESHOLD = 2
    MAX_TIMEOUT = 180  # 3 minutes

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.error_call_back,
                meta={'playwright': True, "playwright_include_page": True}
            )

    async def error_call_back(self, failure):
        if 'playwright_page' in failure.request.meta:
            page = failure.request.meta['playwright_page']
            await page.close()
            self.logger.error(f"Error: {failure}")

    async def parse(self, response, **kwargs):
        items: List[Selector] = response.xpath(self.ITEMS_XPATH)
        page = response.meta['playwright_page']

        for index, item in enumerate(items[:2]):
            item_xpath = self.ITEMS_XPATH + f"[{index + 1}]"

            # Scroll to the current item. This makes sure the item is in view before extracting.
            await page.eval_on_selector(item_xpath, "element => element.scrollIntoView()")

            # Wait for the necessary elements of the item to be visible.
            await page.wait_for_selector(f"{item_xpath}{self.PRICE_XPATH[2:]}", state='visible',
                                         timeout=int(self.MAX_TIMEOUT*1e3))

            # Extract the details.
            price = await page.eval_on_selector(f"{item_xpath}{self.PRICE_XPATH[2:]}", "element => element.textContent")
            title = await page.eval_on_selector(f"{item_xpath}{self.TITLE_XPATH[2:]}", "element => element.textContent")
            link = await page.eval_on_selector(f"{item_xpath}{self.LINK_XPATH[2:]}",
                                               "element => element.getAttribute('href')")
            print(f"{index} ,Price: {price}, Title: {title}, Link: {link}")
            yield response.follow(url=link, callback=self.parse_detail,

                                  meta=dict(playwright=True,
                                            playwright_include_page=True,
                                            price=price,
                                            title=title,
                                            link=link,
                                            ))

        next_page_url = self.get_next_page_url(response)
        if next_page_url:
            yield response.follow(url=next_page_url, callback=self.parse, meta=dict(playwright=True,
                                                                                    playwright_include_page=True,
                                                                                    ))
        if 'playwright_page' in response.meta:
            await response.meta['playwright_page'].close()

    async def parse_detail(self, response: Response, **kwargs):
        description = await response.meta['playwright_page'].eval_on_selector(
            self.DETAIL_XPATH,
            "element => element.textContent")
        title = response.meta.get('title', 'Not found')
        price = response.meta.get('price', 'Not found')
        print(dict(description=description, title=title, price=price))
        yield OlxItem(description=description, title=title, price=price)
        if 'playwright_page' in response.meta:
            await response.meta['playwright_page'].close()

    def get_next_page_url(self, response):
        content = response.xpath(self.ITEMS_XPATH)
        url = response.url
        number: int = get_page_number_from_url(url)

        if not content or number > self.PAGE_THRESHOLD:
            return None

        if number == 0:
            return f"{url}?o=2"

        return url.replace(f'o={number}', f'o={number + 1}')
