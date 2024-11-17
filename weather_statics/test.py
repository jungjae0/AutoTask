import pandas as pd
from urllib.parse import quote
region = quote('가평')
url = f"http://weather-rda.digitalag.kr:5000/?start_date=20241001&end_date=20241004&region={region}&format=csv"

def generate_statics(df, start_date, end_date):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    df['tm'] = pd.to_datetime(df['tm'])
    df['year'] = df['tm'].dt.year
    df['month'] = df['tm'].dt.month
    df['day'] = df['tm'].dt.day

    df['date'] = pd.to_datetime(df[['year', 'month', 'day']])

    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)].reset_index(drop=True)

    df['week_number'] = ((df['date'] - start_date).dt.days // 7) + 1

    weekly_stats = df.groupby('week_number').agg(
        total_precipitation=('sumRn', lambda x: round(x.sum(), 1)),
        average_temperature=('avgTa', lambda x: round(x.mean(), 1)),
        average_windspeed=('avgWs', lambda x: round(x.mean(), 1)),
        average_humid=('avgRhm', lambda x: round(x.mean(), 1)),
        average_sun=('sumGsr', lambda x: round(x.mean(), 1)),
        start_date=('date', 'min'),  # 각 주차별 시작 날짜
        end_date=('date', 'max')
    ).reset_index()

    weekly_stats['week_number'] = weekly_stats.apply(
        lambda x: f"{int(x['week_number'])} ({x['start_date'].strftime('%m.%d')} ~ {x['end_date'].strftime('%m.%d')})",
        axis=1
    )
    weekly_stats = weekly_stats.drop(columns=['start_date', 'end_date'])


    starat_end = f"전체({start_date.strftime('%m.%d')} ~ {end_date.strftime('%m.%d')})"
    rsum = weekly_stats['total_precipitation'].sum()
    tavg = round(weekly_stats['average_temperature'].mean(), 1)
    wavg = round(weekly_stats['average_windspeed'].mean(), 1)
    havg = round(weekly_stats['average_humid'].mean(), 1)
    savg = round(weekly_stats['average_sun'].mean(), 1)

    new_row = pd.DataFrame({
        'week_number': [starat_end],
        'total_precipitation': [rsum],
        'average_temperature': [tavg],
        'average_windspeed': [wavg],
        'average_humid': [havg],
        'average_sun': [savg],
    })

    weekly_stats = pd.concat([new_row, weekly_stats], ignore_index=True)

    weekly_stats.columns = ['주', '강우량\n(mm)', '평균 기온\n(°C)', '평균풍속\n(m/s)', '평균 상대습도\n(%)', '평균 일사량\n(MJ/m²/day)']

    return weekly_stats

df = pd.read_csv(url, encoding='cp949')

df = df.rename(columns={'date': 'tm', 'hum': 'avgRhm', 'temp' : 'avgTa', 'wind' : 'avgWs', 'sun_Qy': 'sumGsr', 'rain' : 'sumRn'})

week = generate_statics(df, '2024-10-01', '2024-10-04')
print(week)
