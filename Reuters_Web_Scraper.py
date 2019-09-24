from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pytz import all_timezones, timezone
import json, boto3, os


def from_Eastern_to_SGT(Eastern):

    Singapore = timezone('Asia/Singapore')
    SingaporeTime = Eastern.astimezone(Singapore)
    strTime = SingaporeTime.strftime('%Y-%m-%d %H:%M:%S')
    jsonTitle = SingaporeTime.strftime('%Y-%m-%d_%H_%M_%S')
    return strTime, jsonTitle

def scraper():
    monthkey = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,
                'November': 11, 'December': 12}

    s3_client = boto3.client('s3')
    # specify the url

    quote_page = 'https://www.reuters.com/news/archive/gca-foreignexchange?view=page&page=2&pageSize=10'
    #quote_page = 'https://www.reuters.com/news/archive/gca-foreignexchange?view=page&page=4&pageSize=10'

    # query the website and return the html to the variable page
    page = urlopen(quote_page)

    # parse the html using beautiful soap and store in variable `soup`
    soup = BeautifulSoup(page, 'html.parser')

    #price_box = soup.find_all('div', attrs={'class': "o-teaser o-teaser--article o-teaser--small o-teaser--has-image o-teaser--opinion js-teaser"})
    price_box = soup.find_all('div', attrs={'class' : "story-content"})

    for tag in price_box:
        HL_dict = {}
        #print(tag.text)
        contentURL = tag.find('a')['href']
        contentURL = "https://www.reuters.com"+contentURL

        try:
            summary = tag.find('p')
            summary = summary.text
        except AttributeError as ae:
            headline = tag.text
            headline = headline.split("\n\n\n\t\t\t\t\t\t\t\t")[-1]
            summary = headline.split("\n\n\n")[0]



        subpage = urlopen(contentURL)
        subsoup = BeautifulSoup(subpage, 'html.parser')
        EDTstr = subsoup.find('div', attrs={'class': "ArticleHeader_date"}).text
        DATE = EDTstr.split("/")[0]
        DATEList = DATE.split(" ")
        tIME = EDTstr.split("/")[1]
        tIMEList = tIME.split(" ")
        # print(DATEList)
        # print(tIMEList)

        strYear = int(DATEList[2])
        strMonth = monthkey[DATEList[0]]
        strDay = int(DATEList[1].split(",")[0])
        strHour = int(tIMEList[2].split(':')[0])
        strMinute = int(tIMEList[2].split(':')[-1])
        EDTDate = datetime(strYear, strMonth, strDay, 0, 0, 0)
        if tIMEList[3] == 'PM':
            strHour = strHour + 12
        EDTDate = EDTDate + timedelta(hours=strHour, minutes=strMinute)
        print(EDTDate)

        EDT_End = datetime(2019, 11, 10, 2, 0, 0) + timedelta(hours=12)
        Eastern = timezone('US/Eastern')
        if datetime.now() > EDT_End:
            EST = Eastern.localize(EDTDate, is_dst=False)
        else:
            EST = Eastern.localize(EDTDate, is_dst=True)

        SGT, fileName = from_Eastern_to_SGT(EST)
        HL_dict['curr_time'] = SGT
        HL_dict['link'] = contentURL
        HL_dict['headline'] = summary

        outfile = 'Reuters_%s.json' % (fileName)
        outpath = '/home/ubuntu/News_Headline_Scraper/Headlines/%s' % (outfile)
        print(HL_dict)

        with open(outpath, 'w') as of:
            json.dump(HL_dict, of)












if __name__ == '__main__':
    scraper()