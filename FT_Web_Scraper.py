# import libraries

from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pytz import all_timezones, timezone
import json, boto3, os

def scraper():

    s3_client = boto3.client('s3')
    # specify the url
    #quote_page = 'https://www.ft.com/currencies'
    quote_page = 'https://www.ft.com/currencies?format=&page=2'

    # query the website and return the html to the variable page
    page = urlopen(quote_page)

    # parse the html using beautiful soap and store in variable `soup`
    soup = BeautifulSoup(page, 'html.parser')

    #price_box = soup.find_all('div', attrs={'class': "o-teaser o-teaser--article o-teaser--small o-teaser--has-image o-teaser--opinion js-teaser"})
    price_box = soup.find_all('div', attrs={'class' : "o-teaser__heading"})
    HeadLines = []
    for tag in price_box:
        HL = {}
        headline = tag.text
        headline = headline.split('\xa0')[0]
        if headline.split(" ")[-1] == "Premium":
            headline = headline.replace(" Premium", "")
        HL['headline'] = headline
        contentURL = tag.find('a')['href']
        if contentURL.split('://')[0] == 'http':
            HL['link'] = contentURL
        else:
            HL['link'] = "https://www.ft.com%s" %(contentURL)
        HeadLines.append(HL)


    time_box = soup.find_all('time', attrs={'class' : "o-date o-teaser__timestamp"})
    i = 0
    for timetag in time_box:
        HLDict = HeadLines[i]
        UTC = datetime.strptime(timetag['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        SGT = UTC + timedelta(hours=8)
        filename = SGT.strftime('%Y-%m-%d_%H_%M_%S')
        SGT = SGT.strftime('%Y-%m-%d %H:%M:%S')

        HLDict['curr_time'] = SGT
        print(HLDict)

        outfile = 'FT_%s.json' % (filename)
        outpath = '/home/ubuntu/News_Headline_Scraper/Headlines/%s' % (outfile)
        with open(outpath, 'w') as of:
            json.dump(HLDict, of)

        # s3_client.upload_file(outpath, 'team-ai-lambda', "News_Headline/" + outfile)
        #
        # if os.path.isfile(outpath):
        #     os.remove(outpath)
        i = i + 1






if __name__ == '__main__':
    scraper()
