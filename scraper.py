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
import sys


BASE_URL = "https://www.renthop.com/search/nyc"
NUM_PAGES = 230
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
                try:
                    soup = get_soup_for_page(page+1)
                    urls.extend(get_page_listing_urls(soup))
                except:
                    break
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

def write_row(f, availability_date, listing_url):
    string = str(listing_url) + "," + str(availability_date)
    print>>f, string

def get_listings_with_availability(output_file):
        listing_urls = get_listing_urls()
        url_dates = {}
        f = open(output_file, 'a')
        for listing_url in listing_urls:
            try:
                availability_date = get_listing_availability(listing_url)
                url_dates[listing_url] = availability_date
                write_row(f, availability_date, listing_url)
            except:
                continue
        f.close()
        return url_dates

def get_availability_stats(listings_file,filtered_listings_file, stats_file):
        listings_and_availability = get_listings_with_availability(listings_file)
        total_listings = len(listings_and_availability)
        histogram = defaultdict(int)
        late_enough_dates = 0
        late_enough_listings = {}
        filtered_listings_output = open(filtered_listings_file, "w")
        for listing in listings_and_availability:
                avail_date = listings_and_availability[listing]
                histogram[avail_date] += 1
                if (avail_date >= EARLIEST_DATE):
                        late_enough_dates += 1
                        late_enough_listings[listing] = avail_date
                        write_row(filtered_listings_output,avail_date,listing)
        filtered_listings_output.close()
        stats_output = open(stats_file,"w")
        print>> stats_output, "Total number of listings: "
        print>> stats_output,str(total_listings)
        print>> stats_output,("Total number of listings with availability starting after " + str(EARLIEST_DATE))
        print>> stats_output,str(late_enough_dates)
        print>> stats_output,"Percentage: "
        print>> stats_output,str((float(late_enough_dates)/float(total_listings)))
        print>> stats_output,str(histogram)
        stats_output.close()

def main():
    listings_file = sys.argv[1] # store individual listings results here
    filtered_listings_file = sys.argv[2] # store output listings results here
    stats_file = sys.argv[3]
    get_availability_stats(listings_file,filtered_listings_file,stats_file)

main()
