
BOT_NAME = "olx"

SPIDER_MODULES = ["olx.spiders"]
NEWSPIDER_MODULE = "olx.spiders"

ROBOTSTXT_OBEY = True

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"


ERROR_DIR = "./errors"

DOWNLOAD_DELAY = 3


ITEM_PIPELINES = {
    "olx.pipelines.OlxPipeline": 300,
}

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'


DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}


# Database settings

DATABASE = {
    'host': 'localhost',
    'port': '27017',
    'db': 'olx',
    'collection': 'items',
    'user': 'root',
    'password': 'ScrapyUtxMongo2023!'
}

DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

MIDDLEWARES = {
    'scrapy_playwright.middleware.PlaywrightMiddleware': 0,
}

# Playwright settings


PLAYWRIGHT_BROWSER_TYPE = "firefox" # you can use 'firefox' or 'webkit' if you prefer

PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,  # Show the browser
    "devtools": False,   # Open devtools for debugging
    "timeout": int(50e3),  # 10 s
}

COOKIES_ENABLED = False

CONCURRENT_REQUESTS = 16

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 120000  # 120 seconds

LOG_LEVEL = 'INFO'

