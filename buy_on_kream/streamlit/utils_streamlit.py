import streamlit as st
from PIL import Image, ImageOps
import requests
from io import BytesIO
import json


def process_image(url, background_color=(240, 240, 240), crop=False):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).convert("RGBA") 
    background = Image.new("RGBA", img.size, background_color + (255,)) 
    img = Image.alpha_composite(background, img).convert("RGB")#.resize((300, 300)) 

    if crop == True:
        width, height = img.size
        if width != height:
            min_size = min(width, height)
            left = (width - min_size) // 2
            top = (height - min_size) // 2
            right = left + min_size
            bottom = top + min_size
            img = img.crop((left, top, right, bottom))

    return img


def load_fonts():
    st.markdown(
        """
        <script>
        (function(d) {
            var config = {
            kitId: 'exz4xvk', 
            scriptTimeout: 3000,
            async: true
            },
            h=d.documentElement,t=setTimeout(function(){h.className=h.className.replace(/\bwf-loading\b/g,"")+" wf-inactive";},config.scriptTimeout),tk=d.createElement("script"),f=false,s=d.getElementsByTagName("script")[0],a;h.className+=" wf-loading";tk.src='https://use.typekit.net/'+config.kitId+'.js';tk.async=true;tk.onload=tk.onreadystatechange=function(){a=this.readyState;if(f||a&&a!="complete"&&a!="loaded")return;f=true;clearTimeout(t);try{Typekit.load(config)}catch(e){}};s.parentNode.insertBefore(tk,s)
        })(document);
        </script>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <style>
            body {
                font-family: "pretendard", sans-serif;
            }
            .pretendard-medium {
                font-family: "pretendard", sans-serif;
                font-weight: 500; /* Medium */
            }
            .pretendard-semibold {
                font-family: "pretendard", sans-serif;
                font-weight: 600; /* SemiBold */
            }
            .pretendard-bold {
                font-family: "pretendard", sans-serif;
                font-weight: 700; /* Bold */
            }
            .pretendard-extrabold {
                font-family: "pretendard", sans-serif;
                font-weight: 800; /* ExtraBold */
            }

            .static-button {
                background-color: #f2f2f2; /* 연한 회색 배경 */
                color: gray; /* 검은색 글씨 */
                padding: 3px 8px 2px 8px; /* 내부 여백 */
                font-size: 12px; /* 글꼴 크기 */
                border-radius: 50px; /* 둥근 모서리 */
                display: inline-block; /* 크기 조정 가능 */
                text-align: center;
                width: fit-content; /* 내용 크기에 맞게 조정 */
                font-family: "pretendard", sans-serif; 
                font-weight: 500;
                margin-top: 3px;
            }

            .custom-button {
                background-color: #ffffff; /* 연한 회색 배경 */
                color: gray; /* 검은색 글씨 */
                border: none; /* 테두리 없음 */
                padding: 12px 20px; /* 내부 여백 */
                font-size: 16px; /* 글꼴 크기 */
                font-weight: bold; /* 글씨 굵게 */
                border-radius: 30px; /* 둥근 모서리 */
                cursor: pointer; /* 마우스 커서 변경 */
                transition: background-color 0.3s ease, transform 0.1s ease; /* 부드러운 전환 효과 */
                display: inline-block; /* 크기 조정 가능 */
                text-align: center;
            }
            /* 호버 효과 */
            .custom-button:hover {
                background-color: #BDBDBD; /* 조금 더 진한 회색 */
            }
            /* 클릭(활성화) 효과 */
            .custom-button:active {
                background-color: #9E9E9E; /* 더 진한 회색 */
                transform: scale(0.98); /* 살짝 눌리는 효과 */
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def format_price(value):
    if isinstance(value, int):
        return f"{value:,}원"
    elif isinstance(value, str):
        return int(value.replace(',', '').replace('원', ''))
    else:
        return None


def round_price(n):
    return (n // 100) * 100


def format_round_price(value):
    value = (value // 100) * 100
    return f"{value:,}원"


def contents(df_tag, session_state, items_per_page):
    pages = (len(df_tag) - 1) // items_per_page + 1
    items_per_row = items_per_page / 2; rows = len(df_tag)//items_per_row + 1

    if session_state not in st.session_state:
        st.session_state[session_state] = 0

    idx_start = items_per_page * st.session_state[session_state]; idx_end = idx_start + items_per_page
    now = df_tag.loc[idx_start:idx_end]

    for r in range(2):
        idx_start2 = idx_start + r*items_per_row
        idx_end2 = idx_start2 + items_per_row

        now2 = df_tag.loc[idx_start2:idx_end2]
        image = [process_image(url_img) for url_img in now2['img_kream']]

        cols = st.columns(5)
        for i, c in enumerate(cols):
            with c:
                try:
                    st.image(image[i])
                except:
                    st.write("")

    col_prev, col_next = st.columns([9, 1])

    with col_prev:
        if st.session_state[session_state] > 0:
            if st.button("이전"):
                st.session_state[session_state] -= 1
                st.rerun()

    with col_next:
        if st.session_state[session_state] < pages - 1:
            if st.button("다음"):
                st.session_state[session_state] += 1
                st.rerun()


def format_title(text, max_length=30):
    if len(text) > max_length:
        return text[:max_length] + "..."  # 길면 줄여서 ... 추가
    else:
        space_needed = max_length - len(text)
        return text + '' + "&nbsp;" * space_needed  # 짧으면 공백 추가
