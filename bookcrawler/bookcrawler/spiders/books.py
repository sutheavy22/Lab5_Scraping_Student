
import scrapy


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]


    max_pages = 2

    def parse(self, response):
     
        books = response.css("article.product_pod")

        for book in books:
            relative_url = book.css("h3 a::attr(href)").get()

            if relative_url:
                book_url = response.urljoin(relative_url)

            
                yield response.follow(
                    book_url,
                    callback=self.parse_book
                )

        next_page = response.css("li.next a::attr(href)").get()

        current_page = response.meta.get("page_number", 1)

        if next_page and current_page < self.max_pages:
            yield response.follow(
                next_page,
                callback=self.parse,
                meta={"page_number": current_page + 1}
            )

    def parse_book(self, response):

        title = response.css(
            "div.product_main h1::text"
        ).get(default="").strip()

        price = response.css(
            "p.price_color::text"
        ).get(default="").strip()

        availability = response.css(
            "p.instock.availability::text"
        ).getall()

        availability = " ".join(
            value.strip() for value in availability
        ).strip()

        rating = response.css(
            "p.star-rating::attr(class)"
        ).get(default="")

        description = response.css(
            "#product_description ~ p::text"
        ).get(default="").strip()

        category = response.css(
            "ul.breadcrumb li:nth-child(3) a::text"
        ).get(default="").strip()

        text = " ".join(
            value for value in [
                title,
                description,
                category,
                availability
            ] if value
        )

        yield {
            "doc_id": response.url.split("/")[-2],
            "title": title,
            "text": text,
            "description": description,
            "url": response.url,
            "category": category,
            "price_gbp": price,
            "rating": rating,
            "availability": availability,
            "source": "Books to Scrape"
        }
