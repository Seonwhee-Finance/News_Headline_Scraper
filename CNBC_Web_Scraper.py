# import libraries

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
    monthkey = {'Jan' : 1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12 }
    s3_client = boto3.client('s3')
    # specify the url
    #quote_page = 'https://www.cnbc.com/real-estate/'
    #quote_page = 'https://www.cnbc.com/economy/'
    #quote_page = 'https://www.cnbc.com/banks/'
    #quote_page = 'https://www.cnbc.com/finance/'
    quote_page = 'https://www.cnbc.com/investing/'

    # query the website and return the html to the variable page
    page = urlopen(quote_page)

    # parse the html using beautiful soap and store in variable `soup`
    soup = BeautifulSoup(page, 'html.parser')

    # Take out the <div> of name and get its value
    #name_box = soup.find('tbody', attrs={'class': 'data-table-body'})
    #name_box = soup.find_all('body')

    # name = name_box.text.strip()  # strip() is used to remove starting and trailing spaces
    #
    # print(name)

    # get the index price

    # price_box = soup.find('div', attrs={'class': 'stx-subholder'})
    price_box = soup.find_all('div', attrs={'class': 'Card-titleContainer'})
    for tags in price_box:
        HL_dict = {}
        HeadLine = tags.find('div').text
        Link = tags.find('a')['href']
        subpage = urlopen(Link)
        subsoup = BeautifulSoup(subpage, 'html.parser')
        try:
            EDTstr = subsoup.find('time').text
            EDTstr = EDTstr.split('Published ')[-1]
            EDTstrList = EDTstr.split(' ')
            if EDTstrList[-1] == 'ago':
                continue
            else:

                strYear = int(EDTstrList[3])
                strMonth = monthkey[EDTstrList[1]]
                strDay = int(EDTstrList[2])
                strHour = int(EDTstrList[5].split(':')[0])
                strMinute = int(EDTstrList[5].split(':')[-1])
                EDTDate = datetime(strYear, strMonth, strDay, 0, 0, 0)
                if EDTstrList[6] == 'PM':
                    strHour = strHour + 12
                EDTDate = EDTDate + timedelta(hours=strHour, minutes=strMinute)

                Eastern = timezone('US/Eastern')
                if EDTstrList[-1] == 'EST':
                    EST = Eastern.localize(EDTDate, is_dst=False)
                elif EDTstrList[-1] == 'EDT':
                    EST = Eastern.localize(EDTDate, is_dst=True)

                SGT, fileName = from_Eastern_to_SGT(EST)
                HL_dict['curr_time'] = SGT
                HL_dict['link'] = Link
                HL_dict['headline'] = HeadLine

                outfile = 'CNBC_%s.json' % (fileName)
                outpath = '/home/ubuntu/News_Headline_Scraper/Headlines/%s' % (outfile)



                print(HL_dict)

                with open(outpath, 'w') as of:
                    json.dump(HL_dict, of)

                # s3_client.upload_file(outpath, 'team-ai-lambda', "News_Headline/" + outfile)
                #
                # if os.path.isfile(outpath):
                #     os.remove(outpath)
        except AttributeError as ae:
            continue







if __name__ == '__main__':
    scraper()
