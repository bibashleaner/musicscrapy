# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MusicItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    artist = scrapy.Field()
    key = scrapy.Field()
    difficulty = scrapy.Field()
    lyrics_with_chords = scrapy.Field()
