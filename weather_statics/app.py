import streamlit as st
from datetime import date, timedelta, datetime
import pandas as pd
from io import BytesIO

def select_asos_station(key):
    station_data = pd.read_csv("./station.csv")
    stations = station_data['지점명'].unique()

    station_name = st.selectbox('지역을 선택하세요', stations, key=f'st_{key}')
    station_code = station_data[station_data['지점명'] == station_name]['지점'].values[0]
    return station_name, station_code


def select_agri_region(key):
    region_data = pd.read_csv(r"./region_info.csv", encoding='cp949')
    do_names = region_data['도명'].unique()
    do_name = st.selectbox('도를 선택하세요', do_names, key=f'do_{key}')
    spot_names = region_data[region_data['도명'] == do_name]['지점명'].unique()
    spot_name = st.selectbox('지점을 선택하세요', spot_names, key=f'spot_{key}')
    do_spot_name = f"{do_name} {spot_name}"
    region_name = region_data[(region_data['도명'] == do_name) & (region_data['지점명'] == spot_name)]['input_region'].values[0]

    return do_spot_name, region_name


def select_date(key):
    # 날짜 입력 받기 (형식: 'YYYY-MM-DD')
    col1, col2 = st.columns(2)
    with col1:
        start_date_input = st.text_input("날짜를 입력하세요 (형식: YYYY-MM-DD)", "2024-05-17", key=f'sd_{key}')
    with col2:
        end_date_input = st.text_input("날짜를 입력하세요 (형식: YYYY-MM-DD)", "2024-11-07", key=f'ed_{key}')

    # 날짜 문자열을 datetime 객체로 변환
    try:
        start_date = datetime.strptime(start_date_input, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_input, '%Y-%m-%d')
        return start_date, end_date
    except ValueError:
        st.write("잘못된 날짜 형식입니다. 'YYYY-MM-DD' 형식으로 입력하세요.")




def get_asos(station_code, start_date, end_date):
    start_year = start_date.year
    end_year = end_date.year

    if start_year == end_year:
        url = f"https://raw.githubusercontent.com/jungjae0/Data-Weather/refs/heads/main/weather_data/{station_code}/{start_year}.csv"
        df = pd.read_csv(url)
    else:
        df = pd.DataFrame()
        for year in range(start_year, end_year + 1):
            url = f"https://raw.githubusercontent.com/jungjae0/Data-Weather/refs/heads/main/weather_data/{station_code}/{year}.csv"
            each = pd.read_csv(url)
            df = pd.concat([df, each])

    return df

def get_agri(region, start_date, end_date):
    start_date = start_date.strftime('%Y%m%d')
    end_date = end_date.strftime('%Y%m%d')
    from urllib.parse import quote
    region = quote(region)
    url = f"http://weather-rda.digitalag.kr:5000/?start_date={start_date}&end_date={end_date}&region={region}&format=csv"

    df = pd.read_csv(url, encoding='cp949')
    df = df.rename(
        columns={'date': 'tm', 'hum': 'avgRhm', 'temp': 'avgTa', 'wind': 'avgWs', 'sun_Qy': 'sumGsr', 'rain': 'sumRn'})
    return df

def generate_statics(df, start_date, end_date):


    try:
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

        csv_data = weekly_stats.to_csv(index=False, encoding='utf-8-sig')

        # BytesIO를 사용하여 CSV를 바이트 형식으로 변환
        buffer = BytesIO()
        buffer.write(csv_data.encode('utf-8-sig'))  # CSV 데이터에 utf-8-sig 인코딩 적용
        buffer.seek(0)  # 버퍼의 시작으로 이동

        return weekly_stats, buffer
    except:
        st.warning("날짜를 제대로 입력하세요.")

def get_aws(uploaded_file):


    if uploaded_file is not None:
        # CSV 파일 읽기
        df = pd.read_csv(uploaded_file)

        # 데이터프레임 미리보기
        st.write("파일 내용:")
        st.write(df.head())

        # 날짜 형식 선택
        date_format = st.radio("날짜 형식을 선택하세요:", ["단일 날짜 열", "연, 월, 일 열로 나누어진 날짜"])

        if date_format == "단일 날짜 열":
            # 사용자가 날짜 열을 선택할 수 있도록 하는 선택 상자
            date_column = st.selectbox("날짜 열을 선택하세요", df.columns)

            if date_column:
                # 날짜 열이 문자열일 경우 날짜 형식으로 변환
                df[date_column] = pd.to_datetime(df[date_column], errors='coerce')

        elif date_format == "연, 월, 일 열로 나누어진 날짜":
            # 연, 월, 일 열 선택
            col1, col2, col3 = st.columns(3)
            with col1:
                year_column = st.selectbox("연도 열을 선택하세요", df.columns)
            with col2:
                month_column = st.selectbox("월 열을 선택하세요", df.columns)
            with col3:
                day_column = st.selectbox("일 열을 선택하세요", df.columns)

            if year_column and month_column and day_column:
                # 연, 월, 일을 결합하여 하나의 날짜로 생성
                df['date'] = pd.to_datetime(
                    df[year_column].astype(str) + '-' + df[month_column].astype(str) + '-' + df[day_column].astype(str),
                    errors='coerce')

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            avgta_column = st.selectbox("평균 온도 열을 선택하세요", df.columns)
        with col2:
            avgws_column = st.selectbox("평균 풍속 열을 선택하세요", df.columns)
        with col3:
            avgrhm_column = st.selectbox("평균 상대습도 열을 선택하세요", df.columns)
        with col4:
            sumgsr_column = st.selectbox("평균 일사량 열을 선택하세요", df.columns)
        with col5:
            sumrn_column = st.selectbox("총 강우량 열을 선택하세요", df.columns)
        # 경고 조건: 동일한 열이 선택되었는지 확인
        selected_columns = [avgta_column, avgws_column, avgrhm_column, sumgsr_column, sumrn_column, date_column]

        # 동일한 열을 선택하면 경고 메시지 표시
        if len(selected_columns) != len(set(selected_columns)):
            st.warning("같은 열이 여러 번 선택되었습니다. 다른 열을 선택하세요.")
            show_data = False  # 오류 발생 시 데이터프레임 표시 안 함
        else:
            show_data = True  # 오류 없을 때만 데이터프레임을 표시

        # 날짜 열이 포함되었으면 해당 날짜 열을 포함한 데이터프레임 생성
        if date_format == "단일 날짜 열" and date_column:
            selected_columns = [date_column] + [avgta_column, avgws_column, avgrhm_column, sumgsr_column, sumrn_column]
        elif date_format == "연, 월, 일 열로 나누어진 날짜" and 'date' in df.columns:
            selected_columns = ['date'] + [avgta_column, avgws_column, avgrhm_column, sumgsr_column, sumrn_column]

        # 오류가 없을 때만 데이터프레임 생성
        if show_data:
            # 최종적으로 선택한 열만 포함한 데이터프레임 생성
            filtered_df = df[selected_columns]

            # 선택된 열들만 보여주기
            st.write("선택된 데이터:")
            st.write(filtered_df.head())

            filtered_df.columns = ['tm', 'avgTa', 'avgWs', 'avgRhm', 'sumGsr', 'sumRn']



            return filtered_df

def download_result(df, start_date, end_date, station_name, key):
    weekly_stats, csv_data = generate_statics(df, start_date, end_date)

    col1, col2 = st.columns(2)

    with col1:
        file_name = st.text_input("파일명을 입력하세요 (확장자 없이)", f"{station_name}_생육기간별_기상자료", key=key)
    with col2:
        full_file_name = f"{file_name}.csv"
        st.download_button(
            label="CSV 파일 다운로드",
            data=csv_data,
            file_name=full_file_name,
            mime="text/csv"
        )

    st.write(weekly_stats)


def get_minus_et(aws_df, asos_df, start_date, end_date):
    pass


def page_aws():
    st.title("시험지 배지 AWS 기상 자료 생성")
    uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

    aws_key = "AWS"
    if uploaded_file is not None:
        # 버튼이 클릭될 때만 실행하도록 조건 추가
        aws_df = get_aws(uploaded_file)

        aws_station_name = st.text_input("지역 이름을 입력하세요", "서울")

        aws_start_date, aws_end_date = select_date(aws_key)
        if aws_df is not None:

            try:
                download_result(aws_df, aws_start_date, aws_end_date, aws_station_name, 'AWS')

            except:
                st.warning("오류: 데이터가 올바르게 반환되지 않았습니다. 입력 값을 확인해주세요.")


def page_asos():
    asos_key = "ASOS"
    st.title("ASOS 기상 자료 생성")
    asos_station_name, asos_station_code = select_asos_station(asos_key)
    asos_start_date, asos_end_date = select_date(asos_key)
    asos_df = get_asos(asos_station_code, asos_start_date, asos_end_date)
    download_result(asos_df, asos_start_date, asos_end_date, asos_station_name, asos_key)

def page_agri():
    agri_key = "AGRI"
    st.title("농업기상 자료 생성")
    do_spot_name, agri_region_name = select_agri_region(agri_key)
    agri_start_date, agri_end_date = select_date(agri_key)
    agri_df = get_agri(agri_region_name, agri_start_date, agri_end_date)
    download_result(agri_df, agri_start_date, agri_end_date, do_spot_name, agri_key)

def main():
    st.set_page_config(layout="wide")
    col1, col2 = st.columns(2)
    with col1:
        page_asos()
        page_agri()
    with col2:
        page_aws()







if __name__ == '__main__':
    main()