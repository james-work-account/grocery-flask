import os
import re
import search.curl_wrapper as cw

import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from search.json_selector_helper import JsonSelectorHelper
from search.shop_details import ShopDetails

CHROMEDRIVER_PATH = os.environ.get('CHROMEDRIVER_PATH', '/usr/local/bin/chromedriver')
GOOGLE_CHROME_BIN = os.environ.get('GOOGLE_CHROME_BIN', '/usr/bin/google-chrome')

max_length = 10
options = Options()
options.add_argument(
    'user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-extensions')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1280x1696')
options.add_argument('--hide-scrollbars')
options.add_argument('--single-process')
options.add_argument('--ignore-certificate-errors')
options.headless = True
driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=options)


def _get_tesco_searches(search_term) -> ShopDetails:
    return ShopDetails(
        search_term=search_term,
        requires_webdriver=False,
        shop_name='TESCO',
        url=f'https://www.tesco.com/groceries/en-GB/search?query={search_term}',
        not_found_css_selector='.empty-section',
        items_list_selector='.product-list > li',
        price_css_selector='.price-control-wrapper',
        offer_selector='div > div.product-tile.has-promotion > div > div.promotions-wrapper.hidden-medium > ul > li > a > div > span.offer-text, .product-info-message',
        title_css_selector='a[data-auto="product-tile--title"]',
    )


def _get_morrisons_searches(search_term) -> ShopDetails:
    return ShopDetails(
        search_term=search_term,
        requires_webdriver=False,
        shop_name='MORRISONS',
        url=f'https://groceries.morrisons.com/search?entry={search_term}',
        not_found_css_selector='p[class$=noResultsFoundMessage], div[class$=resourceNotFound]',
        items_list_selector='.fops-shelf > li',
        price_css_selector='.fop-price',
        offer_selector='a.promotion-offer > span',
        name_css_selector='.fop-title span',
        weight_css_selector='.fop-catch-weight',
        requires_requests=True
    )


def _get_waitrose_searches(search_term) -> ShopDetails:
    return ShopDetails(
        search_term=search_term,
        requires_webdriver=False,
        shop_name='WAITROSE',
        url=f'https://www.waitrose.com/ecom/shop/search?&searchTerm={search_term}',
        not_found_css_selector='[class^=alternativeSearch]',
        items_list_selector='.container-fluid > .row > article',
        price_css_selector='span[data-test=product-pod-price] > span',
        offer_selector='[data-test=link-offer]',
        name_css_selector='[class^=name_]',
        weight_css_selector='[class^=size]',
    )


def _get_aldi_searches(search_term) -> ShopDetails:
    return ShopDetails(
        search_term=search_term,
        requires_webdriver=False,
        shop_name='ALDI',
        url=f'https://www.aldi.co.uk/search?text={search_term}',
        not_found_css_selector='p[class$=no-results]',
        items_list_selector='#products-tab .hover-item',
        price_css_selector='.category-item__price',
        offer_selector='.js-price-discount',
        price_split=True,
        title_css_selector='.category-item__title',
    )


def _get_sainsburys_searches(search_term) -> ShopDetails:
    return ShopDetails(
        search_term=search_term,
        requires_webdriver=True,
        shop_name='SAINSBURYS',
        url=f'https://www.sainsburys.co.uk/gol-ui/SearchDisplayView?filters[keyword]={search_term}',
        not_found_css_selector='div[class$=no-results]',
        items_list_selector='.ln-o-section:not(.header-fixed-subheading) li.pt-grid-item',
        price_css_selector='[data-test-id=pt-retail-price]',
        offer_selector='.promotion-message, .pd__label',
        currency_symbol='£',
        title_css_selector='[data-test-id=product-tile-description]',
        wait_condition=EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test-id=search-results-title]')),
        json_selector=JsonSelectorHelper(
            json_url=f"https://www.sainsburys.co.uk/groceries-api/gol-services/product/v1/product?page_size={max_length}&filter%5Bkeyword%5D=",
            product_array_selector="products",
            name_selector="name",
            price_selector="retail_price.price",
            promotions_array_selector="promotions",
            promotions_text_selector="strap_line",
            weight_selector=None,
        )
    )


def _get_asda_searches(search_term) -> ShopDetails:
    return ShopDetails(
        search_term=search_term,
        requires_webdriver=True,
        shop_name='ASDA',
        url=f'https://groceries.asda.com/search/{search_term}',
        not_found_css_selector='.no-result',
        items_list_selector='#main-content > main > div.search-page-content > div:nth-child(4) > div > div.co-product-list > ul li.co-item',
        price_css_selector='.co-product__price',
        offer_selector='.link-save-banner-large__config',
        name_css_selector='[data-auto-id=linkProductTitle]',
        weight_css_selector='.co-product__volume',
        wait_condition=EC.text_to_be_present_in_element((By.CSS_SELECTOR, '[class^=search-content-header]'),
                                                        'search results'),
        json_selector=JsonSelectorHelper(
            json_url='https://groceries.asda.com/api/items/search?productperpage=' + str(max_length) + '&keyword=',
            product_array_selector='items',
            name_selector='itemName',
            price_selector='price',
            promotions_text_selector='promoDetailFull',
            brand_selector='brandName',
            weight_selector='weight',
        )
    )


def _get_coop_searches(search_term) -> ShopDetails:
    return ShopDetails(
        search_term=search_term,
        requires_webdriver=True,
        shop_name='CO-OP',
        url=f'https://shop.coop.co.uk/search?term={search_term}',
        not_found_css_selector='.search-results .search-results--no-results',
        items_list_selector='.product-list--grid > article',
        price_css_selector='.product-card--info--price',
        offer_selector='.product-promo--name',
        title_css_selector='.product-card--name',
        wait_condition=EC.text_to_be_present_in_element((By.CSS_SELECTOR, '.page-header__title'),
                                                        'Results for'),
        json_selector=JsonSelectorHelper(
            json_url='https://retailer-api-coop.foodieservices.com/v1/search/products?',
            product_array_selector='data.products',
            name_selector='name.en',
            price_selector='prices.clicks_unit_price',
            promotions_text_selector='details.trade_item_marketing_message.en',
            body={"language": "en", "tree": "coophomedelivery", "store_id": "17eda196-0394-4cf5-9053-a7652fc76671",
                  "match_phrase": {"phrase": f"{search_term}", "language": "en"},
                  "meta": {"pagination": {"page": 1, "page_size": 10}}},
            headers=[
                "content-type:application/json",
                "dg-api-key:25a9de6b-9648-45f1-af4b-40dd8320f0ee",
                "dg-organization-id:291564910276510723",
                "origin:https://shop.coop.co.uk"
            ],
        )
    )


def _get_bandm_searches(search_term) -> ShopDetails:
    return ShopDetails(
        search_term=search_term,
        requires_webdriver=True,
        shop_name='B&M',
        url=f'https://www.bmstores.co.uk/search?query={search_term}',
        not_found_css_selector='.search-results .search-results--no-results',
        items_list_selector='[data-algolia="hits"] > ul > li',
        price_css_selector='a > div > span',
        offer_selector='.badge',
        title_css_selector='h2',
        wait_condition=EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'strong[data-algolia="query"]'),
                                                        search_term),
        json_selector=JsonSelectorHelper(
            json_url='https://mv7e2a3yql-dsn.algolia.net/1/indexes/*/queries?x-algolia-application-id=MV7E2A3YQL&x-algolia-api-key=MDg5YWJkM2RkYTA1YjBjOTdlZDU3ZTBiMzhhNzM0OThkYmM3ODFmNTk2YzNiZmRkZmMwZTMyMzc5ZjBkNzZmM2ZpbHRlcnM9JTI4c3RhdHVzJTNBYXBwcm92ZWQlMjkrQU5EK3B1Ymxpc2hkYXRlKyUzQysxNjA0NzY3MjU2K0FORCslMjhleHBpcnlkYXRlKyUzRSsxNjA0NzY3MjU2K09SK2V4cGlyeWRhdGUrJTNEKy0xJTI5&',
            product_array_selector='results.0.hits',
            name_selector='title',
            price_selector='productsellprice',
            promotions_text_selector='promotion',
            body={"requests": [{"indexName": "prod_bmstores", "params": f"query={search_term}&hitsPerPage={max_length}"}]},
            headers=[
                'Referer:https://www.bmstores.co.uk/'
            ]
        ),
    )


def shops(search_term):
    return [
        _get_tesco_searches(search_term),
        _get_waitrose_searches(search_term),
        _get_aldi_searches(search_term),
        _get_sainsburys_searches(search_term),
        _get_asda_searches(search_term),
        _get_coop_searches(search_term),
        _get_bandm_searches(search_term),
        _get_morrisons_searches(search_term),
    ]


def load_page_source(shop: ShopDetails) -> str:
    if shop.requires_webdriver:
        driver.get(shop.url)
        # Some shops fetch results after the page has loaded - wait for a certain condition to pass, otherwise timeout and move on.
        if shop.wait_condition is not None:
            WebDriverWait(driver, 10).until(shop.wait_condition)
        return driver.page_source
    else:
        if shop.requires_requests:
            req = requests.get(shop.url, headers={
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Safari/537.36",
            })
            return req.text
        else:
            return cw.make_request(shop.url, ["user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.99 Safari/537.36"], False)


def search_page_source(page_source: str, shop: ShopDetails) -> str:
    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        # Look for something on the page that indicates that no results are found.
        # If len(condition) is 0, the "no results found" text is not present and you can assume there are results on the page.
        if len(soup.select(shop.not_found_css_selector)) == 0:
            # Create a PrettyTable
            t = PrettyTable(['Item', 'Price', 'Offers'])
            # Iterate over items
            for i, elem in enumerate(soup.select(shop.items_list_selector)):
                # In case lots of items are returned, you probably only need the first few
                if i >= max_length:
                    break

                title = ''
                # Title should be in the format `Name Quantity`
                # Some shops combine them together (use title_css_selector), others have them separate (use name_css_selector and weight_css_selector)
                if shop.title_css_selector is not None:
                    title = elem.select_one(shop.title_css_selector).text.replace('\n', ' ').strip()
                if shop.name_css_selector is not None and shop.weight_css_selector is not None:
                    name = elem.select_one(shop.name_css_selector).text.strip()
                    weight = elem.select_one(shop.weight_css_selector).text.strip()
                    title = f'{name} {weight}'
                try:
                    price = elem.select_one(shop.price_css_selector).text.replace('\n', ' ').strip()
                except AttributeError:
                    continue
                # In case the price isn't the only text in the element returned by the price_css_selector
                if shop.price_split:
                    price = price.split(' ')[0]

                offer = ' '.join([el.getText().strip() for el in
                                  set(elem.select(shop.offer_selector))])

                t.add_row([title, price, offer])
            return t.get_html_string(sortby='Price', sort_key=lambda row: _format_price(row[0]))
        else:
            return f'No results found for {shop.search_term}'
    except (NoSuchElementException, TimeoutException):
        return f'Error finding product: {shop.search_term}'


def search_json(shop: ShopDetails):
    if shop.json_selector is not None:
        t = PrettyTable(['Item', 'Price', 'Offers'])
        if shop.json_selector.body is not None:
            js = cw.make_request(
                url=shop.json_selector.full_url(shop.search_term),
                headers=['Accept: application/json', 'Content-Type: application/json'] + shop.json_selector.headers,
                is_json=True,
                body=shop.json_selector.body
            )
        else:
            js = cw.make_request(
                url=shop.json_selector.full_url(shop.search_term),
                headers=shop.json_selector.headers,
                is_json=True
            )

        products = _get_value(shop.json_selector.product_array_selector.split('.'), js)
        if len(products) > 0:
            for i, product in enumerate(products):
                if i == max_length:
                    break

                name = _get_value(shop.json_selector.name_selector.split('.'), product)
                title = re.sub("\\[\\d]", "", name)  # remove random number from coop
                if shop.json_selector.weight_selector is not None:
                    weight = _get_value(shop.json_selector.weight_selector.split('.'), product)
                    title = f'{title} {weight}'
                if shop.json_selector.brand_selector is not None:
                    try:
                        brand = product[shop.json_selector.brand_selector]
                        title = f'{brand} {title}'
                    except KeyError:
                        pass

                price = _get_value(shop.json_selector.price_selector.split("."), product)
                if not isinstance(price, str):
                    price = "£{:.2f}".format(float(price))

                if shop.json_selector.promotions_array_selector is not None:
                    offer = ", ".join(
                        [_get_value(shop.json_selector.promotions_text_selector.split("."), o) for o in
                         product[shop.json_selector.promotions_array_selector]])
                else:
                    offer = _get_value(shop.json_selector.promotions_text_selector.split("."), product)
                    if str(offer) == '0':
                        offer = ''

                t.add_row([title, price, offer])

            return t.get_html_string(sortby='Price', sort_key=lambda row: _format_price(row[0]))
        else:
            return f'No results found for {shop.search_term}'
    else:
        raise Exception("No JSON selector")


def _get_value(arr, inp) -> str:
    """
    Recursively iterate through a JSON structure until a value is found
    :param arr: array of selectors to iterate through
    :param inp: input json
    :return: Value found through recursive search or KeyError
    """
    if len(arr) == 0:
        return ''
    if len(arr) == 1:
        try:
            return inp[arr[0]]
        except TypeError:
            return inp[int(arr[0])]
    head, *tail = arr
    try:
        return _get_value(tail, inp[head])
    except TypeError:
        return _get_value(tail, inp[int(head)])


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

