class ShopDetails:
    def __init__(self,
                 shop_name: str,
                 url: str,
                 not_found_css_selector: str,
                 items_list_selector: str,
                 price_css_selector: str,
                 offer_selector: str,
                 price_split: bool = False,
                 name_css_selector: str = None,
                 weight_css_selector: str = None,
                 title_css_selector: str = None,
                 wait_condition: any = None,
                 accept_cookies_css_selector: str = None):
        self.shop_name = shop_name
        self.url = url
        self.not_found_css_selector = not_found_css_selector
        self.items_list_selector = items_list_selector
        self.price_css_selector = price_css_selector
        self.offer_selector = offer_selector
        self.price_split = price_split
        self.name_css_selector = name_css_selector
        self.weight_css_selector = weight_css_selector
        self.title_css_selector = title_css_selector
        self.wait_condition = wait_condition
        self.accept_cookies_css_selector = accept_cookies_css_selector
