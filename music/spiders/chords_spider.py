import scrapy
from scrapy_playwright.page import PageMethod
from music.items import MusicItem
import re

class ChordsSpider(scrapy.Spider):
    name = "songs"
    allowed_domains = ["e-chords.com"]
    
    def start_requests(self):
        # Generate A-Z artist index URLs
        base_url = "https://www.e-chords.com/top-tabs/{}"
        for letter in "abcdefghijklmnopqrstuvwxyz":
            url = base_url.format(letter)
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "#top-overall-artists")
                    ],
                    "handle_httpstatus_list": [404],
                },
                callback=self.parse_artist_list
            )

    def parse_artist_list(self, response):
        # Extract artist links
        artist_links = response.css('#top-overall-artists a::attr(href)').getall()
        for link in artist_links[:100]:  # Limit for demonstration
            yield response.follow(
                link,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "table.tbtab")
                    ],
                    "handle_httpstatus_list": [404],
                },
                callback=self.parse_artist
            )
        
        # Pagination handling
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield response.follow(
                next_page,
                meta=response.meta,
                callback=self.parse_artist_list
            )

    def parse_artist(self, response):
        # Extract first 5 song links
        song_links = response.css('#top-songs a::attr(href)').getall()
        for link in song_links[:5]:
            yield response.follow(
                link,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div#cifra")
                    ],
                    "handle_httpstatus_list": [404],
                },
                callback=self.parse_song
            )

    def parse_song(self, response):
        item = MusicItem()
        item["url"] = response.url
    
        # Title
        title = response.css('h1.component-song-show-header__song-title::text').get()
        if title:
            item["title"] = title.strip()
        else:
            item["title"] = response.css("h1#titl::text").get() or ""
    
        # Artist
        artist = response.css('h2.component-bordered-heading a::text').get()
        if artist:
            item["artist"] = artist.strip()
        else:
            item["artist"] = response.css("h2#artl::text").get() or ""
    
        # Key - new implementation
        key_new = response.css('button.key-change span.key::text').get()
        if key_new:
            item["key"] = key_new.strip()
        else:
            # Fallback to old method
            item["key"] = ""
            metadata_rows = response.css("div.cifra-top tr")
            for row in metadata_rows:
                label = row.css("td::text").get()
                if label and "Key" in label:
                    item["key"] = row.css("td:last-child::text").get() or ""
                    break
    
        # Difficulty - updated implementation
        difficulty_new = response.css('span.component-song-show-header_level_label::text').get()
        if difficulty_new:
            item["difficulty"] = difficulty_new.strip()
        else:
            # Fallback to old method
            item["difficulty"] = ""
            metadata_rows = metadata_rows or response.css("div.cifra-top tr")
            for row in metadata_rows:
                label = row.css("td::text").get()
                if label and "Difficulty" in label:
                    item["difficulty"] = row.css("td:last-child::text").get() or ""
                    break
    
        # Lyrics with chords
        lyrics_container = response.css('div.component-song-show-chord-content')
        if lyrics_container:
            lyrics_html = lyrics_container.css('pre').get()
            if lyrics_html:
                cleaned_lyrics = re.sub(
                    r'<div class="popup[^>]*>.*?</div>', 
                    '',
                    lyrics_html,
                    flags=re.DOTALL
                )
                cleaned_lyrics = re.sub(r' style="[^"]*"', '', cleaned_lyrics)
                cleaned_lyrics = re.sub(r'<span[^>]*></span>', '', cleaned_lyrics)
                item["lyrics_with_chords"] = cleaned_lyrics.strip()
            else:
                item["lyrics_with_chords"] = ""
        else:
            item["lyrics_with_chords"] = response.css("div#cifra_tab").get() or ""
    
        yield item