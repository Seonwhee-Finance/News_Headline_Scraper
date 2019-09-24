import json, boto3, os
from glob import glob

def task_manager():
    s3_client = boto3.client('s3')
    Curr_dir = glob("./Headlines/*")
    Old_dir = glob("./Headlines_old/*")

    Old_dir_File = []

    for oneFile in Old_dir:
        Old_dir_File.append(oneFile.split("/")[-1])

    for currFile in Curr_dir:
        if currFile.split("/")[-1] in Old_dir_File:
            print("Delete " + currFile)
            if os.path.isfile(currFile):
                os.remove(currFile)
        else:
            print("Upload To s3:// /News_Headline/" + currFile.split("/")[-1])
            s3_client.upload_file(currFile, '', "News_Headline/" + currFile.split("/")[-1])



if __name__ == '__main__':
    task_manager()