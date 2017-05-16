# Strategy:
# Use requests library to do a search
# using the paging functionality in the url, loop through each page
# for each page, use beautifulsoup to get a list of listings to click into
# then for each these listings, find the available date
# if the available date is after the desired time, then keep the url. otherwise, discard
# output a list of urls with the required characteristics
# https://www.renthop.com/search/nyc?location_search=&bedrooms%5B%5D=2&min_price=3000&max_price=4500&q=&neighborhoods_str=7&sort=hopscore&page=1&search=1
# class: search-photo-layout

from bs4 import BeautifulSoup
import requests

BASE_URL = "https://www.renthop.com/search/nyc"
#NUM_PAGES = 295
NUM_PAGES = 5

def get_soup_for_page(page):
        payload = {'bedrooms':'2','min_price':'3000','max_price':'4500','neighborhoods_str':'7','page':str(page)}
        r = requests.get(BASE_URL,payload)
        soup = BeautifulSoup(r.text,"html.parser")
        return soup

def get_page_listing_urls(soup):
        links = soup.find_all("a",class_="search-photo-layout")
        urls = []
        for link in links:
                urls.append(link.get('href'))
        return urls

def get_listing_urls():
        urls = []
        for page in range(NUM_PAGES):
                soup = get_soup_for_page(page+1)
                urls.extend(get_page_listing_urls(soup))
        return urls


def parse_individual_listing():
        pass

def filter_listings_by_availability():
        pass

print(get_listing_urls())

