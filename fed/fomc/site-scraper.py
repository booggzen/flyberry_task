from bs4 import Beautifulsoup
import requests

FED_CALENDAR_PAGE = "http://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"

def _grab_page(url):
    return requests.get(url)
    
    

_grab_page(FED_CALENDAR_PAGE)