class JsonSelectorHelper:
    def __init__(self,
                 json_url: str,
                 product_array_selector: str,
                 name_selector: str,
                 price_selector: str,
                 promotions_text_selector: str,
                 img_selector: str = None,
                 img_fn: str = None,
                 img_search_term: str = None,
                 img_base_url: str = None,
                 link: str = None,
                 body: dict = None,
                 headers=None,
                 promotions_array_selector: str = None,
                 weight_selector: str = None,
                 brand_selector: str = None,
                 base_url: str = None,
                 ):
        if headers is None:
            headers = []
        self.json_url = json_url
        self.product_array_selector = product_array_selector
        self.name_selector = name_selector
        self.price_selector = price_selector
        self.promotions_text_selector = promotions_text_selector
        self.body = body
        self.headers = headers
        self.promotions_array_selector = promotions_array_selector
        self.weight_selector = weight_selector
        self.brand_selector = brand_selector
        self.link = link
        self.base_url = base_url
        self.img_selector = img_selector
        self.img_fn = img_fn
        self.img_search_term = img_search_term
        self.img_base_url = img_base_url

    def full_url(self, search_term: str):
        return self.json_url + search_term
