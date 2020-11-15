from search.json_selector_helper import JsonSelectorHelper


class ShopDetails:
    def __init__(self,
                 search_term: str,
                 requires_webdriver: bool,
                 shop_name: str,
                 url: str,
                 not_found_css_selector: str,
                 items_list_selector: str,
                 price_css_selector: str,
                 offer_selector: str,
                 currency_symbol: str = '',
                 price_split: bool = False,
                 name_css_selector: str = None,
                 weight_css_selector: str = None,
                 title_css_selector: str = None,
                 wait_condition: any = None,
                 accept_cookies_css_selector: str = None,
                 json_selector: JsonSelectorHelper = None,
                 requires_requests: bool = False,
                 min_length: int = None,
                 ):
        self.min_length = min_length
        self.requires_requests = requires_requests
        self.search_term = search_term
        self.requires_webdriver = requires_webdriver
        self.shop_name = shop_name
        self.url = url
        self.not_found_css_selector = not_found_css_selector
        self.items_list_selector = items_list_selector
        self.price_css_selector = price_css_selector
        self.offer_selector = offer_selector
        self.currency_symbol = currency_symbol
        self.price_split = price_split
        self.name_css_selector = name_css_selector
        self.weight_css_selector = weight_css_selector
        self.title_css_selector = title_css_selector
        self.wait_condition = wait_condition
        self.accept_cookies_css_selector = accept_cookies_css_selector
        self.json_selector = json_selector
