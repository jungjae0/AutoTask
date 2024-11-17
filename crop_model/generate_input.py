import pandas as pd
import os
import tqdm
import numpy as np
import math

def single(stn_Ids: int):
    data_dir = "../output/cache_weather_model"
    filenames = [x for x in os.listdir(data_dir) if x.endswith(".csv") and x.startswith(f"{stn_Ids}_")]

    single = pd.DataFrame()
    for filename in filenames:
        each = pd.read_csv(os.path.join(data_dir, filename))
        single = pd.concat([single, each], ignore_index=True)

    return single

def calculate_column(stn_Ids: int, latitude: int, altitude: int):
    single_weather = single(stn_Ids)

    single_weather['sumRn'] = single_weather['sumRn'].fillna(0)

    #### 일사량 & 증발산량  null 처리 ####
    lati = latitude  # 북위
    alti = altitude  # 해발고도
    height = 10

    u_2 = single_weather['avgWs'] * 4.87 / np.log(67.8 * height - 5.42)
    P = 101.3 * ((293 - 0.0065 * alti) / 293) ** 5.26
    delta = single_weather['avgTa'].apply(lambda x: 4098 * (0.6108 * np.exp((17.27 * x) / (x + 237.3))) / (x + 237.3) ** 2)
    gamma = 0.665 * 10 ** (-3) * P
    u_2_cal = 1 + 0.34 * u_2  # P
    Q = delta / (delta + gamma * u_2_cal)  # Q
    R = gamma / (delta + gamma * u_2_cal)  # R
    S = 900 / (single_weather['avgTa'] + 273) * u_2  # S
    e_s = single_weather['avgTa'].apply(lambda x: 0.6108 * np.exp((17.27 * x) / (x + 237.3)))
    e_a = single_weather['avgRhm'] / 100 * e_s
    e = e_s - e_a  # e_s-e_a
    doi = single_weather['doy']  # day of year
    dr = doi.apply(lambda x: 1 + 0.033 * np.cos(2 * 3.141592 / 365 * x))
    smsingle_weather_delta = doi.apply(lambda x: 0.409 * np.sin(2 * 3.141592 / 365 * x - 1.39))
    theta = lati * math.pi / 180
    w_s = np.arccos(-np.tan(theta) * smsingle_weather_delta.apply(lambda x: np.tan(x)))

    Ra = 24 * 60 / math.pi * 0.082 * dr * \
         (w_s * smsingle_weather_delta.apply(lambda x: math.sin(x)) *
          np.sin(theta) +
          np.cos(theta) *
          smsingle_weather_delta.apply(lambda x: math.cos(x)) *
          w_s.apply(lambda x: math.sin(x)))
    N = 24 / math.pi * w_s
    Rs = (0.25 + 0.5 * single_weather['sumSsHr'] / N) * Ra
    Rso = (0.75 + 2 * 10 ** (-5) * alti) * Ra
    Rs_Rso = Rs / Rso  # Rs/Rso
    R_ns = 0.77 * Rs
    R_nl = 4.903 * 10 ** (-9) * (single_weather['avgTa'] + 273.16) ** 4 * (0.34 - 0.14 * e_a ** (0.5)) * (
            1.35 * Rs_Rso - 0.35)
    G = 0
    ET = ((0.408) * (delta) * (R_ns - R_nl - G) + (gamma) * (900 / (single_weather['avgTa'] + 273)) * u_2 * (e)) / (
            delta + gamma * (1 + 0.34 * u_2))

    single_weather['sumGsr'] = single_weather['sumGsr'].fillna(round(R_ns, 3))
    single_weather['sumSmlEv'] = single_weather['sumSmlEv'].fillna(round(ET, 3))

    single_weather['sumGsr'] = single_weather['sumGsr'].apply(lambda x: x if x > 1 else 2)

    single_weather = single_weather.fillna(0)
    single_weather.columns = ['year', 'month', 'day', 'doy', 'radn', 'maxt', 'mint',
                              'rain', 'evap', 'tavg', 'humid', 'wind', 'hr_radn']

    return single_weather

####----------Aqua Crop----------####
def create_aqua(df, stn_Nm: str, aqua_dir):
    df = df[['day', 'month', 'year', 'mint', 'maxt', 'rain', 'evap', 'wind', 'humid', 'radn']]
    df.columns = ['Day', 'Month', 'Year', 'Tmin(C)', 'Tmax(C)', 'Prcp(mm)', 'Et0(mm)', 'Wind at 10m', 'RHmean',
                  'Solar rad']
    df.to_csv(os.path.join(aqua_dir, f"{stn_Nm}_weather.csv"), index=False)

####----------DSSAT----------####
def create_dssat(df, stn_Nm: str, latitude: int, altitude: int, longitude:int, dssat_dir):
    filename = stn_Nm

    output_weather_filename = os.path.join(dssat_dir, f"{filename}_weather.wth")

    site = filename[0:4].upper()

    meta_info = f"""$WEATHER: {site}2023

*GENERAL
@Latitude Longitud  Elev Zone    TAV  TAMP REFHT WNDHT SITE
   {latitude:6.3f}  {longitude:6.3f}   {altitude:6.3f}   Am  -99.0 -99.0 -99.0 -99.0 {site}
@WYR  WFIRST   WLAST
   0 1980000 2000365
@PEOPLE

@ADDRESS

@METHODS

@INSTRUMENTS

@PROBLEMS

@PUBLICATIONS

@DISTRIBUTION

@NOTES
Created on day 2023-02-07 at 오후 1:39:54

*DAILY DATA
@  DATE  TMAX  TMIN  RAIN  WIND  SRAD
"""
    with open(output_weather_filename, "w") as fout:
        fout.write(meta_info)
        # 2007001   0.0   0.0  69.1   0.0   0.0
        #  df[['maxt', 'mint', 'wind', 'rain', 'radn', 'year', 'doy']]
        for idx, row in df.iterrows():
            # print(row)
            year = int(row['year'])
            doy = int(row['doy'])
            fout.write(
                f"{year}{doy:03d}{row['maxt']:6.1f}{row['mint']:6.1f}{row['rain']:6.1f}{row['wind'] * 86.4:6.1f}{row['radn']:6.1f}\n")

####----------APSIM----------####
def create_apsim(df, stn_Nm: str, latitude: int, longitude: int, apsim_dir):

    tav = round(df.groupby('year').mean()['tavg'].mean(), 2)
    amp = round((df.groupby('month').max()['tavg'] - df.groupby('month').min()['tavg']).mean(), 2)

    meta_info = f"""[weather.met.weather]
    !Title  =  {stn_Nm}  2007-2020
    latitude  ={latitude}
    Longitude  ={longitude}
    !  TAV  and  AMP  inserted  by  'tav_amp'  on  31/12/2020  at  10:00  for  period  from      1/2007  to  366/2020  (ddd/yyyy)
    tav  =    {tav}  (oC)          !  annual  average  ambient  temperature
    amp  =    {amp}  (oC)          !  annual  amplitude  in  mean  monthly  temperature

    site year day radn maxt mint rain evap
    () () () (MJ/m2) (oC) (oC) (mm) (mm)
    """
    output_weather_filename = os.path.join(apsim_dir, f"{stn_Nm}_weather.txt")
    with open(output_weather_filename, "w") as fout:
        fout.write(meta_info)
        for idx, row in df.iterrows():
            year = int(row['year'])
            doy = int(row['doy'])
            fout.write(f"{stn_Nm} {year} {doy} {row['radn']} {row['maxt']} {row['mint']} {row['rain']} {row['evap']}\n")

####----------Wofost----------####
def creat_wofost(df, stn_Nm: str, latitude: int, altitude: int, longitude: int, wofost_dir):

    for year in range(2007, 2021):
        meta_info = f"""*---------------------------------------------------------*
*   Country: Republic of Korea
*   Station: {stn_Nm}
*      Year: {year}
*    Source: Dep. of Meteorology, Wageningen Agricultural
*            University.
*    Author: Peter Uithol
* Longitude: {str(longitude).replace('.', ' ')} E
*  Latitude: {str(latitude).replace('.', ' ')} N
* Elevation: {int(altitude)} m.
*  Comments: Location Haarweg.
*
*  Columns:
*  ========
*  station number
*  year
*  day
*  irradiation (kJ m-2 d-1)
*  minimum temperature (degrees Celsius)
*  maximum temperature (degrees Celsius)
*  mean wind speed (m s-1)
*  precipitation (mm d-1)
** WCCDESCRIPTION=Republic of Korea, {stn_Nm}
** WCCFORMAT=2
** WCCYEARNR={year}
*---------------------------------------------------------*
{longitude} {latitude} {int(altitude)}. 0 0
"""
        new_filename_s = stn_Nm[0:3]
        new_filename_y = str(year)[1:4]
        output_weather_filename = os.path.join(wofost_dir, f"{new_filename_s}.{new_filename_y}")
        df_year = df[df['year'] == year]
        with open(output_weather_filename, "w") as fout:
            fout.write(meta_info)
            for idx, row in df_year.iterrows():
                year = int(row['year'])
                doy = int(row['doy'])
                fout.write(f"1 {year} {doy} {int(row['radn']*1000)} {row['mint']} {row['maxt']} {row['rain']}\n")

def main():
    output_dir = "../output/iksan"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    aqua_dir = os.path.join(output_dir, "aqua")
    if not os.path.exists(aqua_dir):
        os.makedirs(aqua_dir)

    dssat_dir= os.path.join(output_dir, "dssat")
    if not os.path.exists(dssat_dir):
        os.makedirs(dssat_dir)

    apsim_dir= os.path.join(output_dir, "apsim")
    if not os.path.exists(apsim_dir):
        os.makedirs(apsim_dir)

    wofost_dir= os.path.join(output_dir, "wofost")
    if not os.path.exists(wofost_dir):
        os.makedirs(wofost_dir)

    df_site = pd.read_csv("../output/통계청_정보.csv")
    df_site = df_site[df_site['파일명'] == '전라북도_군산시']
    # for i in tqdm.tqdm(range(len(df_site))):
    #     stn_Ids = df_site['지점코드'].to_list()[i]
    #     stn_Nm = df_site['영문 표기'].to_list()[i]
    #     latitude = df_site['위도'].to_list()[i]
    #     altitude = df_site['고도'].to_list()[i]
    #     longitude = df_site['경도'].to_list()[i]
    #     df = calculate_column(stn_Ids, latitude, altitude)
    #     # Aqua Crop
    #     create_aqua(df, stn_Nm, aqua_dir)
    #     # DSSAT
    #     create_dssat(df, stn_Nm, latitude, altitude, longitude, dssat_dir)
    #     # APSIM
    #     # create_apsim(df, stn_Nm, latitude, longitude, apsim_dir)
    #     # # Wofost
    #     # creat_wofost(df, stn_Nm, latitude, altitude, longitude, wofost_dir)
    #     print(stn_Nm)

    for idx, row in df_site.iterrows():
        stn_Ids = row['지점코드']
        stn_Nm = row['영문 표기']
        latitude = row['위도']
        altitude = row['고도']
        longitude = row['경도']
        df = calculate_column(stn_Ids, latitude, altitude)
        # Aqua Crop
        create_aqua(df, stn_Nm, aqua_dir)
        # DSSAT
        create_dssat(df, stn_Nm, latitude, altitude, longitude, dssat_dir)
        # APSIM
        # create_apsim(df, stn_Nm, latitude, longitude, apsim_dir)
        # # Wofost
        # creat_wofost(df, stn_Nm, latitude, altitude, longitude, wofost_dir)
        print(stn_Nm)


if __name__ == '__main__':
    main()