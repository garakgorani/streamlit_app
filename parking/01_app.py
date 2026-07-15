import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="공영주차장 정보 제공",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 공영주차장 정보 제공 서비스")

uploaded_file = st.file_uploader(
    "공영주차장 CSV 파일을 업로드하세요.",
    type=["csv"]
)

if uploaded_file is not None:

    # -----------------------------
    # CSV 읽기 (인코딩 자동 처리)
    # -----------------------------
    df = None

    for enc in ["utf-8", "utf-8-sig", "cp949", "euc-kr"]:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            st.success(f"파일을 성공적으로 불러왔습니다. (인코딩: {enc})")
            break
        except:
            pass

    if df is None:
        st.error("CSV를 읽을 수 없습니다.")
        st.stop()

    # -----------------------------
    # 위도·경도 처리
    # -----------------------------
    df["위도"] = pd.to_numeric(df["위도"], errors="coerce")
    df["경도"] = pd.to_numeric(df["경도"], errors="coerce")

    # 좌표 없는 데이터 제거
    df = df.dropna(subset=["위도", "경도"])

    if df.empty:
        st.error("위도 또는 경도 데이터가 없습니다.")
        st.stop()

    # -----------------------------
    # 주소 검색
    # -----------------------------
    st.subheader("🔍 주소 검색")

    keyword = st.text_input("주소를 입력하세요")

    if keyword:

        result = df[df["주소"].astype(str).str.contains(keyword, case=False, na=False)]

        if result.empty:
            st.warning("검색 결과가 없습니다.")

        else:

            st.success(f"{len(result)}개의 주차장을 찾았습니다.")

            show = result[[
                "주차장명",
                "주소",
                "기본 주차 요금",
                "추가 단위 요금",
                "평일 운영 시작시각(HHMM)",
                "평일 운영 종료시각(HHMM)"
            ]]

            st.dataframe(show)

    # -----------------------------
    # 지도 생성
    # -----------------------------
    st.subheader("🗺️ 공영주차장 지도")

    center = [
        float(df["위도"].mean()),
        float(df["경도"].mean())
    ]

    m = folium.Map(
        location=center,
        zoom_start=12
    )

    for _, row in df.iterrows():

        popup = folium.Popup(
            f"""
            <b>{row['주차장명']}</b><br><br>

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
            """,
            max_width=300
        )

        tooltip = (
            f"{row['주차장명']}<br>"
            f"{row['주소']}<br>"
            f"기본요금 : {row['기본 주차 요금']}원"
        )

        # 무료 주차장은 초록색, 유료는 파란색
        color = "green" if str(row["유무료구분명"]) == "무료" else "blue"

        folium.Marker(
            location=[float(row["위도"]), float(row["경도"])],
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=650
    )

else:
    st.info("CSV 파일을 업로드하면 서비스를 이용할 수 있습니다.")
