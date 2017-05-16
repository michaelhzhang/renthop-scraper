# Strategy: # Use requests library to do a search
# using the paging functionality in the url, loop through each page
# for each page, use beautifulsoup to get a list of listings to click into
# then for each these listings, find the available date
# if the available date is after the desired time, then keep the url. otherwise, discard
# output a list of urls with the required characteristics
# https://www.renthop.com/search/nyc?location_search=&bedrooms%5B%5D=2&min_price=3000&max_price=4500&q=&neighborhoods_str=7&sort=hopscore&page=1&search=1
# class: search-photo-layout

from bs4 import BeautifulSoup
import requests
from datetime import date
from collections import defaultdict
import datetime


BASE_URL = "https://www.renthop.com/search/nyc"
#NUM_PAGES = 295
NUM_PAGES = 1
EARLIEST_DATE = datetime.date(2017,07,15)

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

def get_listing_soup(listing_url):
        r = requests.get(listing_url)
        soup = BeautifulSoup(r.text,"html.parser")
        return soup

def get_listing_availability(listing_url):
        soup = get_listing_soup(listing_url)
        premap_div = soup.find(id="listing-details-body-premap")
        table_div = premap_div.contents[7]
        subtable = table_div.contents[5].table
        move_in_string = subtable.tr.contents[-2].b.contents[0]
        return date_string_to_date(move_in_string) 

def date_string_to_date(date_string):
        if date_string == "Immediate":
                return date.today()
        else:
                return datetime.datetime.strptime(date_string,"%b %d").replace(year=2017).date()

def get_listings_with_availability():
        listing_urls = get_listing_urls()
        url_dates = {}
        for listing_url in listing_urls:
                availability_date = get_listing_availability(listing_url)
                url_dates[listing_url] = availability_date
        return url_dates

def get_availability_stats():
        listings_and_availability = get_listings_with_availability()
        total_listings = len(listings_and_availability)
        histogram = defaultdict(int)
        late_enough_dates = 0
        for avail_date in listings_and_availability.values():
                histogram[avail_date] += 1
                if (avail_date >= EARLIEST_DATE):
                        late_enough_dates += 1
        print("Total number of listings: ")
        print(total_listings)
        print("Total number of listings with availability starting after " + str(EARLIEST_DATE))
        print(late_enough_dates)
        print("Percentage: ")
        print(float(late_enough_dates)/float(total_listings))
        print(histogram)

get_availability_stats()
