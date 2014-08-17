import codecs
import json
import random
import sys
import time

import lxml.html
import requests
import scraperwiki


class AirbnbScraper:
    def __init__(self, debug=True):
        self.cookies = {}
        self.debug = debug

    def listing_url(self, offset):
        return ('https://m.airbnb.com/api/-/v1/listings/search?location=semarang&number_of_guests=1&offset=%s&guests=1&items_per_page=20'
                % (offset))

    def get(self, url, referer='', min_sleep=30, max_add=120, xhr=False):
        if self.debug:
            print url

        time.sleep(random.randint(0, max_add) + min_sleep)

        headers = {'User-agent': 'Mozilla/5.0 (Linux; U; Android 2.3; en-us) AppleWebKit/999+ (KHTML, like Gecko) Safari/999.9',
                   'referer': referer}
        if xhr:
            headers['x-requested-with'] = 'XMLHttpRequest'

        r = requests.get(url, headers=headers, cookies=self.cookies)
        self.cookies = r.cookies

        return r

    def crawl(self):
        offset = 0
        fields = ['id', 'city', 'picture_url','user_id', 'price', 'price_native', 'lat', 'lng',
        'name', 'smart_location', 'bedrooms', 'state', 'zipcode', 'address', 'property_type',
        'room_type', 'room_type_category', 'picture_count']

        count = 999
        while offset < count:
            r = self.get(self.listing_url(offset), referer='https://m.airbnb.com/s/Bali--Indonesia')

            try:
                js = json.loads(r.content)
                count = js['listings_count']

                if len(js['listings']) == 0:
                    break
                else:
                    for listing in js['listings']:
                        new_listings = [{k: listing['listing'].get(k, None) for k in fields}]
                        scraperwiki.sqlite.save(["id"],new_listings)

                offset += 20
                if self.debug:
                    print "new offset", offset

            except ValueError as e:
                print >> sys.stderr, 'received ValueError:', e
                print >> sys.stderr, 'error: could not parse response'
                sys.exit(1)

if __name__ == "__main__":
    ab = AirbnbScraper()
    ab.crawl()
