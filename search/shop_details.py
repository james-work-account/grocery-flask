from search.json_selector_helper import JsonSelectorHelper


class ShopDetails:
    def __init__(self,
                 search_term: str,
                 max_search_length: int,
                 requires_webdriver: bool,
                 shop_name: str,
                 url: str,
                 not_found_css_selector: str,
                 items_list_selector: str,
                 price_css_selector: str,
                 base_url: str,
                 link_selector: str,
                 offer_selector: str,
                 currency_symbol: str = '',
                 img_selector: str = None,
                 img_fn: str = None,
                 img_search_term: str = None,
                 img_base_url: str = None,
                 price_split: bool = False,
                 name_css_selector: str = None,
                 weight_css_selector: str = None,
                 title_css_selector: str = None,
                 wait_condition: any = None,
                 accept_cookies_css_selector: str = None,
                 json_selector: JsonSelectorHelper = None,
                 requires_requests: bool = False,
                 ):
        self.requires_requests = requires_requests
        self.search_term = search_term
        self.max_search_length = max_search_length
        self.requires_webdriver = requires_webdriver
        self.shop_name = shop_name
        self.url = url
        self.not_found_css_selector = not_found_css_selector
        self.items_list_selector = items_list_selector
        self.price_css_selector = price_css_selector
        self.base_url = base_url
        self.link_selector = link_selector
        self.offer_selector = offer_selector
        self.currency_symbol = currency_symbol
        self.price_split = price_split
        self.name_css_selector = name_css_selector
        self.weight_css_selector = weight_css_selector
        self.title_css_selector = title_css_selector
        self.wait_condition = wait_condition
        self.accept_cookies_css_selector = accept_cookies_css_selector
        self.json_selector = json_selector
        self.img_selector = img_selector
        self.img_fn = img_fn
        self.img_search_term = img_search_term
        self.img_base_url = img_base_url
