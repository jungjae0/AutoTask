import os
import pytz
import pandas as pd
import urllib.request
from datetime import datetime, timedelta

def save_aws(date):
    aws_dir = "./output"

    Site = 85
    Dev = 1
    Year = date[0:4]
    Mon = date[4:6]
    Day = date[6:8]

    aws_url =f'http://203.239.47.148:8080/dspnet.aspx?Site={Site}&Dev={Dev}&Year={Year}&Mon={Mon}&Day={Day}'
    data = urllib.request.urlopen(aws_url)

    df = pd.read_csv(data, header=None)
    df.columns = ['datetime', 'temp', 'hum', 'X', 'X', 'X', 'rad', 'wd', 'X', 'X', 'X', 'X', 'X', 'ws', 'rain', 'maxws', 'bv', 'X']
    drop_cols = [col for col in df.columns if 'X' in col]
    df = df.drop(columns=drop_cols)

    filename = os.path.join(aws_dir, f"{date}.csv")
    df.to_csv(filename, index=False)

    return df