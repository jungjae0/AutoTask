import os
import tqdm
import pandas as pd


def save_aws_weather(output_dir, station_info):
    for idx, row in tqdm.tqdm(station_info.iterrows(), total=len(station_info)):
        code = row['지점코드']
        name = row['지점명']
        file_name = os.path.join(output_dir, f"{name}.csv")
        if not os.path.exists(file_name):
            url = f"https://api.taegon.kr/stations/{code}/?sy=2000&ey=2022&format=csv"
            df = pd.read_csv(url, sep='\\s*,\\s*', engine="python")
            df.columns = [col.strip() for col in df.columns]
            df = df.rename(columns={'tavg': 'temp', 'tmax': 'max_temp', 'tmin': 'min_temp'})
            df['date'] = pd.to_datetime(dict(year=df.year, month=df.month, day=df.day))
            df = df[['date', 'year', 'month', 'day', 'temp', 'max_temp', 'min_temp']]

            df.to_csv(file_name, index=False, encoding='utf-8')