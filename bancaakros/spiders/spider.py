import scrapy

from scrapy.loader import ItemLoader
from ..items import BancaakrosItem
from itemloaders.processors import TakeFirst


class BancaakrosSpider(scrapy.Spider):
	name = 'bancaakros'
	start_urls = ['https://www.bancaakros.it/news.aspx?history=1&Area=NewsList&csrt=18124357394683781511']

	def parse(self, response):
		print(response.body)
		post_links = response.xpath('//ol/li/h4/a')
		for post in post_links:
			date = post.xpath('./text()').get().split('-')[0]
			link = post.xpath('./@href').get()
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date))

		next_page = response.xpath('//span[@class="pagenav"]/a[text()="Succ."]/@href').getall()
		yield from response.follow_all(next_page, self.parse)


	def parse_post(self, response, date):
		title = response.xpath('//div[@class="content-int"]/h1/text()').get()
		description = response.xpath('//div[@class="content-int"]//text()[normalize-space() and not(ancestor::h1)]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BancaakrosItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
