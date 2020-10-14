import json
import multiprocessing
import os
import re
from typing import List

from prettytable import PrettyTable
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from result import Result

CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN', '/usr/bin/google-chrome')


class Search:

    def __init__(self, search_term):
        self.search_term = search_term
        self.results = []
        self.max_length = 10
        # Set up headless browser/driver (and set user-agent to pretend to not be headless)
        self.options = Options()
        self.options.add_argument(
            'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.headless = True
        self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=self.options)
        self.shops = [
            ['TESCO', self._get_tesco_searches()],
            ['MORRISONS', self._get_morrisons_searches()],
            ['WAITROSE', self._get_waitrose_searches()],
            ['ALDI', self._get_aldi_searches()],
            ['SAINSBURYS', self._get_sainsburys_searches()],
            ['ASDA', self._get_asda_searches()],
        ]

    def to_json(self):
        return json.dumps([result.__dict__ for result in self.results])

    @staticmethod
    def check_value(key, dictionary):
        if key in dictionary:
            return dictionary[key]
        else:
            return None

    def do_thing(self, a: List):
        r = self._search_online_shop(
            url=a[1]['url'],
            not_found_css_selector=a[1]['not_found_css_selector'],
            items_list_selector=a[1]['items_list_selector'],
            price_css_selector=a[1]['price_css_selector'],
            offer_selector=a[1]['offer_selector'],
            price_split=self.check_value('price_split', a[1]),
            name_css_selector=self.check_value('name_css_selector', a[1]),
            weight_css_selector=self.check_value('weight_css_selector', a[1]),
            title_css_selector=self.check_value('title_css_selector', a[1]),
            wait_condition=self.check_value('wait_condition', a[1]),
            accept_cookies_css_selector=self.check_value('accept_cookies_css_selector', a[1]),
        )
        result = Result(a[0], r)
        return result

    # def search_all(self):
    #     try:
    #         # Fetch results
    #         pool = multiprocessing.Pool()
    #         self.results = pool.map(self.do_thing, m)
    #         pool.close()
    #         pool.join()
    #         for result in self.results:
    #             print(result.shop_name)
    #         return self.results
    #     except Exception as e:
    #         print(e)

    def _get_tesco_searches(self) -> dict:
        print('Searching Tesco...')
        return {
            'url': f'https://www.tesco.com/groceries/en-GB/search?query={self.search_term}',
            'not_found_css_selector': '.empty-section',
            'items_list_selector': '.product-list > li',
            'price_css_selector': '.price-control-wrapper',
            'offer_selector': 'div > div.product-tile.has-promotion > div > div.promotions-wrapper.hidden-medium > ul > li > a > div > span.offer-text, .product-info-message',
            'title_css_selector': 'a[data-auto="product-tile--title"]',
        }

    def _get_morrisons_searches(self) -> dict:
        print('Searching Morrisons...')
        return {
            'url': f'https://groceries.morrisons.com/search?entry={self.search_term}',
            'not_found_css_selector': 'p[class$=noResultsFoundMessage], div[class$=resourceNotFound]',
            'items_list_selector': '.fops-shelf > li',
            'price_css_selector': '.fop-price',
            'offer_selector': 'a.promotion-offer > span',
            'title_css_selector': '.fop-description',
        }

    def _get_waitrose_searches(self) -> dict:
        print('Searching Waitrose...')
        return {
            'url': f'https://www.waitrose.com/ecom/shop/search?&searchTerm={self.search_term}',
            'not_found_css_selector': '[class^=alternativeSearch]',
            'items_list_selector': '.container-fluid > .row > article',
            'price_css_selector': 'span[data-test=product-pod-price] > span',
            # TODO: Waitrose offer text currently duplicated, need more specific selector
            'offer_selector': '[data-test=link-offer]',
            'title_css_selector': 'header',
            'accept_cookies_css_selector': 'button[data-test=accept-all]',
        }

    def _get_aldi_searches(self) -> dict:
        print('Searching Aldi...')
        return {
            'url': f'https://www.aldi.co.uk/search?text={self.search_term}',
            'not_found_css_selector': 'p[class$=no-results]',
            'items_list_selector': '#products-tab .hover-item',
            'price_css_selector': '.category-item__price',
            'offer_selector': '.js-price-discount',
            'price_split': True,
            'title_css_selector': '.category-item__title',
        }

    def _get_sainsburys_searches(self) -> dict:
        print('Searching Sainsburys...')
        return {
            'url': f'https://www.sainsburys.co.uk/gol-ui/SearchDisplayView?filters[keyword]={self.search_term}',
            'not_found_css_selector': 'div[class$=no-results]',
            'items_list_selector': '.ln-o-section:not(.header-fixed-subheading) li.pt-grid-item',
            'price_css_selector': '[data-test-id=pt-retail-price]',
            'offer_selector': '.promotion-message, .pd__label',
            'title_css_selector': '[data-test-id=product-tile-description]',
            'wait_condition': EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test-id=search-results-title]')),
        }

    def _get_asda_searches(self) -> dict:
        print('Searching Asda...')
        return {
            'url': f'https://groceries.asda.com/search/{self.search_term}',
            'not_found_css_selector': '.no-result',
            'items_list_selector': '#main-content > main > div.search-page-content > div:nth-child(4) > div > div.co-product-list > ul li.co-item',
            'price_css_selector': '.co-product__price',
            'offer_selector': '.link-save-banner-large__config',
            'name_css_selector': '[data-auto-id=linkProductTitle]',
            'weight_css_selector': '.co-product__volume',
            'wait_condition': EC.text_to_be_present_in_element((By.CSS_SELECTOR, '[class^=search-content-header]'),
                                                               'search results'),
        }

    def _search_online_shop(self, url: str, not_found_css_selector: str, items_list_selector: str,
                            price_css_selector: str, offer_selector: str, price_split: bool = False,
                            name_css_selector: str = None,
                            weight_css_selector: str = None, title_css_selector: str = None, wait_condition: any = None,
                            accept_cookies_css_selector: str = None) -> str:
        try:
            self.driver.get(url)
            # Some shops fetch results after the page has loaded - wait for a certain condition to pass, otherwise timeout and move on.
            if wait_condition is not None:
                WebDriverWait(self.driver, 10).until(wait_condition)

            # Some shops ask you to accept cookies before continuing
            if accept_cookies_css_selector is not None:
                try:
                    self.driver.find_element_by_css_selector(accept_cookies_css_selector).click()
                except NoSuchElementException:
                    pass

            # Look for something on the page that indicates that no results are found.
            # If len(condition) is 0, the "no results found" text is not present and you can assume there are results on the page.
            if len(self.driver.find_elements_by_css_selector(not_found_css_selector)) == 0:
                # Create a PrettyTable
                t = PrettyTable(['Item', 'Price', 'Offers'])
                # Iterate over items
                for i, elem in enumerate(self.driver.find_elements_by_css_selector(items_list_selector)):
                    # In case lots of items are returned, you probably only need the first few
                    if i == self.max_length:
                        break

                    title = ''
                    # Title should be in the format `Name Quantity`
                    # Some shops combine them together (use title_css_selector), others have them separate (use name_css_selector and weight_css_selector)
                    if title_css_selector is not None:
                        title = elem.find_element_by_css_selector(title_css_selector).text.replace('\n', ' ').strip()
                    if name_css_selector is not None and weight_css_selector is not None:
                        name = elem.find_element_by_css_selector(name_css_selector).text.strip()
                        weight = elem.find_element_by_css_selector(weight_css_selector).text.strip()
                        title = f'{name} {weight}'
                    price = elem.find_element_by_css_selector(price_css_selector).text.replace('\n', ' ').strip()

                    # In case the price isn't the only text in the element returned by the price_css_selector
                    if price_split:
                        price = price.split(' ')[0]

                    offer = ' '.join([el.get_attribute('textContent').strip() for el in
                                      elem.find_elements_by_css_selector(offer_selector)])

                    t.add_row([title, price, offer])
                return t.get_html_string(sortby='Price', sort_key=lambda row: self._format_price(row[0]))
            else:
                return f'No results found for {self.search_term}'
        except (NoSuchElementException, TimeoutException):
            return f'Error finding product: {self.search_term}'

    @staticmethod
    def _format_price(price: str) -> float:
        """
        format the price string as a float
        :param price: str
        :return: float
        """
        pound_pattern = '[0-9]+(\\.[0-9]{2}|$)'  # matches pounds, e.g. £2 or £2.99
        penny_pattern = '[0-9]+'  # matches pennies, e.g. 65 (to be turned into 0.65 later)
        pound_match = re.search(pound_pattern, price)
        penny_match = re.search(penny_pattern, price)
        if pound_match is not None:
            span = pound_match.span()
            return float(price[span[0]:span[1]])
        if penny_match is not None:
            span = penny_match.span()
            return float(f'0.{price[span[0]:span[1]]}')
        return 0  # Default - if the price doesn't match either regex, return the price unordered

    def _print_results(self) -> None:
        """
        :return: None
        """
        for result in self.results:
            print(f'\n{result.shop_name}')
            print(result.result)
