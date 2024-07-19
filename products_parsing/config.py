marketplaces = [
    'ozon',
    'wildberries',
    'market.yandex',
    'megamarket',
    'lamoda',
    'google',
]

max_websites_count = 2  # не рекомендуется выставлять значение больше 10

max_results_from_website = 5  # максимальное количество товаров, полученное в итоге с одного сайта
# ограничений нет, но при выставлении значения выше скорость выполнения программы увеличивается резко


'''
некоторые сайты возвращают код 403 - не дают доступ в связи с неправдоподобными headers
методом подбора оставлена конфигурация, работающая для большинства случаев

некоторые сайты возвращают код 401, чаще всего делая редирект на страницу с капчей - это обойти невозможно
'''

headers = {
    'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
    # 'Accept-Encoding': "gzip, deflate, br, zstd",
    'Accept-Language': "de,en-US;q=0.7,en;q=0.3",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    'Connection': "keep-alive",
}

websites_css_selectors = {
    'www.citilink.ru': ['a.app-catalog-9gnskf.e1259i3g0', {'name': '.easmdi50.eml1k9j0.app-catalog-lc5se5.e1gjr6xo0', 'price': '.e1j9birj0.e106ikdt0.app-catalog-8hy98m.e1gjr6xo0', 'rating': 'div.e8eovjk0.app-catalog-1uwfsq8.e2kybqa2', 'reviews': 'a.app-catalog-peotpw.e1mnvjgw0', 'review_rating': 'div span span.e1ys5m360.e106ikdt0.app-catalog-rx1cfc.e1gjr6xo0', 'review_comment': '.app-catalog-a9fxyi.eyoh4ac0'}],
    'www.mvideo.ru': ['a.product-title__text.product-title--clamp', {'name': 'h1.title', 'price': '.price__main-value', 'rating': 'span.rating-value.medium', 'reviews': 'a.rating-reviews.ng-star-inserted', 'review_rating': 'div.total-rating', 'review_comment': 'div.review-text'}],
    'www.dns-shop.ru': ['a.catalog-product__name.ui-link.ui-link_black', {'name': 'h1.product-card-top__title', 'price': 'div.product-buy__price', 'rating': 'a.product-card-top__rating', 'reviews': 'a.product-card-top__rating', 'review_rating': 'div div div div div div.opinion-rating-slider', 'review_comment': 'div.ow-opinion__text'}],
    'www.vseinstrumenti.ru': ['a.-dp5Dd.clamp-3.buZF02', {'name': 'h1.typography.heading.v3.-no-margin', 'price': 'p.typography.heading.v2.-no-margin', 'rating': 'div div div.BJoVux div.rating input', 'reviews': 'section.pOjh3i.TCE984 div div div a.base-button.-small.-primary.-link.-no-paddings', 'review_rating': 'a.a', 'review_comment': 'div[data-qa="comments"]'}],
    'www.technopark.ru': ['a.product-card-link.product-card-big__title.product-card-link--cover-container.product-card-labels__blur', {'name': 'h1.tp-typography.tp-typography--v-heading-2.tp-typography--w-medium.tp-typography--align-left.tp-heading', 'price': 'div div div div div div div div div.product-prices__price', 'rating': 'div.product-page-reviews-badge__badge', 'reviews': '[data-test-id="product-page-nav_product-otzyvy"]', 'review_rating': 'div.nuxt-review-card__rating', 'review_comment': 'div.nuxt-review-card__text'}],
    'ru-mi.com': ['div.main-card.main-card--catalog h3 a.main-card__title-link', {'name': 'h1.product__title-h', 'price': 'div.product-buy__current.product-buy-current.price', 'rating': 'a.a', 'reviews': 'a.s-tab__btn.s-tab__btn--active', 'review_rating': 'div div div div div.rating__stars.rating__stars--xs', 'review_comment': 'div.reviews__text.g-text'}],
    'www.rbt.ru': []
}
