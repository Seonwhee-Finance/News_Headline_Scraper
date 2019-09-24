# import libraries

from glob import glob

import json, boto3, os


def uploader():

    s3_client = boto3.client('s3')

    fileList = glob('/home/ubuntu/News_Headline_Scraper/Headlines/*.json')
    #fileList = glob('/home/ubuntu/News_Headline_Scraper/Headlines/CNBC*.json')

    # time_box = soup.find_all('time', attrs={'class' : "o-date o-teaser__timestamp"})

    for fileName in fileList:
        outfile = fileName.split('/')[-1]


        s3_client.upload_file(fileName, '', "News_Headline/" + outfile)

        # if os.path.isfile(outpath):
        #     os.remove(outpath)







if __name__ == '__main__':
    uploader()
