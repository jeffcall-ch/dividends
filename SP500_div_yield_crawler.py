from bs4 import BeautifulSoup
import requests
import re

class SP500(object):
    def __init__(self):
        pass

    def find_number_percent(self, input_text):
        words = input_text.split(" ")
        found_percentages = []
        for word in words:
            if word.find("%") != -1:
                # append float to list of found items
                found_percentages.append(float((word[:word.find("%")])))
        return found_percentages

    # find the meta tag which holds the Dividend Yield x.xx% value
    def get_dividend_yield(self): 
        page = requests.get('https://www.multpl.com/s-p-500-dividend-yield')

        # Create a BeautifulSoup object
        soup = BeautifulSoup(page.text, 'html.parser')

        found_percentage_values = []
        metatags = soup.find_all('meta',attrs={'name':'description'})
        for tag in metatags:
            current_content = tag.get('content')
            self.find_number_percent(current_content)
            found_percentage_values.extend(self.find_number_percent(current_content))
        if len(found_percentage_values) == 0:
                raise ValueError('Could not crawl Dividend Yield x.xx% value from https://www.multpl.com/s-p-500-dividend-yield')
        if len(found_percentage_values) > 1:
                raise ValueError('Several Dividend Yield x.xx% value found from https://www.multpl.com/s-p-500-dividend-yield. Refine code!')
        # print(found_percentage_values[0])
        return found_percentage_values[0]