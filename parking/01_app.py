import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="공영주차장 정보", page_icon="🅿️", layout="wide")

st.title("🅿️ 공영주차장 정보 제공")

uploaded_file = st.file_uploader("CSV 파일 업로드", type="csv")

if uploaded_file:

    # ------------------------
    # CSV 읽기
    # ------------------------
    df = None

    for enc in ["utf-8", "utf-8-sig", "cp949", "euc-kr"]:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            break
        except:
            pass

    if df is None:
        st.error("CSV를 읽을 수 없습니다.")
        st.stop()

    st.success("CSV 업로드 완료!")

    # ------------------------
    # 주소 검색
    # ------------------------

    st.subheader("🔍 주소 검색")

    keyword = st.text_input("주소 입력")

    if keyword:

        result = df[df["주소"].astype(str).str.contains(keyword, na=False)]

        if result.empty:

            st.warning("검색 결과가 없습니다.")

        else:

            st.success(f"{len(result)}개의 주차장이 검색되었습니다.")

            show = result[
                [
                    "주차장명",
                    "주소",
                    "기본 주차 요금",
                    "추가 단위 요금",
                    "평일 운영 시작시각(HHMM)",
                    "평일 운영 종료시각(HHMM)"
                ]
            ]

            st.dataframe(show)

    # ------------------------
    # 지도
    # ------------------------

    st.subheader("🗺️ 공영주차장 지도")

    center = [
        df["위도"].mean(),
        df["경도"].mean()
    ]

    m = folium.Map(
        location=center,
        zoom_start=12
    )

    for _, row in df.iterrows():

        popup = f"""
        <h4>{row['주차장명']}</h4>

        <b>주소</b><br>
        {row['주소']}<br><br>

        <b>기본요금</b><br>
        {row['기본 주차 요금']}원 /
        {row['기본 주차 시간(분 단위)']}분<br><br>

        <b>추가요금</b><br>
        {row['추가 단위 요금']}원 /
        {row['추가 단위 시간(분 단위)']}분<br><br>

        <b>운영시간</b><br>
        {row['평일 운영 시작시각(HHMM)']} ~
        {row['평일 운영 종료시각(HHMM)']}
        """

        tooltip = f"""
        {row['주차장명']}<br>
        {row['주소']}<br>
        기본요금 : {row['기본 주차 요금']}원
        """

        folium.Marker(
            location=[row["위도"], row["경도"]],
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=650
    )
