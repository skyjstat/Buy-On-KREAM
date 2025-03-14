import streamlit as st
st.set_page_config(
    page_title="크똑소: Buy On KREAM",
    page_icon="👟"
)
from utils_streamlit import load_fonts, process_image, format_round_price, format_title, to_json
from details import details_kream, details_ns, details_mss
import pandas as pd
import sys
import os
import algpy
# sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils_module.utils import shoes_sizes_near

load_fonts()

def get_path(relative_path):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
    return os.path.normpath(os.path.join(BASE_DIR, relative_path)) 


# Title
st.image(get_path("img/title.png"))
st.markdown("""<p class="pretendard-semibold" style="font-size:24px; text-align: center; margin-top:0px">크림에서 똑똑하게 소비하는 방법!</p>""", unsafe_allow_html=True)

st.markdown("---")


# Filter
with st.sidebar:
    st.write(""); st.write(""); st.write(""); st.write(""); st.write(""); st.write("")

    with st.form(key="form_settings"): 
        col1, col2 = st.columns([1, 1])
        gender = col1.selectbox("성별", ['여성', '남성'])
        size = col2.selectbox("사이즈", [str(s) for s in range(220, 325, 5)], index=4)
        featherL, featherR = st.slider("사이즈 업다운", min_value=-2, max_value=2, step=1, value=(-1,2))
        submitted = st.form_submit_button("적용")


# Load & Process Data
item, info = algpy.data_prep(gender, size, featherL, featherR)
df = algpy.tag_rows(item, info, size, featherL, featherR)



################# --------------------------------------------------------------------------------------------------------------------------
### STREAMLIT ### --------------------------------------------------------------------------------------------------------------------------
################# --------------------------------------------------------------------------------------------------------------------------

for ss in ["phase11", "phase12", "phase21", "phase22"]:
    if f"id_{ss}" not in st.session_state:
        st.session_state[f"id_{ss}"] = None


def contents(df_tag, session_state, items_per_page=10):
    pages = (len(df_tag) - 1) // items_per_page + 1
    items_per_row = items_per_page / 2; rows = len(df_tag)//items_per_row + 1

    if session_state not in st.session_state:
        st.session_state[session_state] = 0

    idx_start = items_per_page * st.session_state[session_state]; idx_end = idx_start + items_per_page
    now = df_tag.loc[idx_start:idx_end]

    for r in range(2):
        idx_start2 = idx_start + r * items_per_row
        idx_end2 = idx_start2 + items_per_row - 1

        now2 = df_tag.loc[idx_start2:idx_end2]

        id_kream = now2['id_kream'].tolist()
        image = [process_image(url_img) for url_img in now2['img_kream']]
        title = now2['item_ko'].tolist()
        rep_size = now2['kream_rep_size'].tolist()
        rep_price = [format_round_price(p) for p in now2['kream_rep_price']]

        cols = st.columns(5)
        for i, c in enumerate(cols):
            with c:
                try:
                    st.image(image[i])
                    st.markdown(f"""
                                <div>
                                    <p class="pretendard-semibold" style="font-size:12px; margin-bottom:6px; margin-top:0px;">{format_title(title[i])}</p>
                                    <p>
                                    <span class="pretendard-medium" style="font-size:12px; background-color:#f2f2f2; padding:3.5px 7px 3.5px 7px; border-radius:5px; color:gray">{rep_size[i]}</span>
                                    <span style="font-size:0.5px">ㅤ</span>
                                    <span class="pretendard-semibold" style="font-size:13px;">{rep_price[i]}</span>
                                    </p>
                                </div> 
                                """, unsafe_allow_html=True)
                                
                    if st.button("상세정보", key=f"details_{session_state}_{id_kream[i]}", use_container_width=True):
                        st.session_state[f"id_{session_state}"] = id_kream[i]
                        st.rerun()
                except:
                    st.write("")        

    col_prev, col_next = st.columns([9, 1])

    with col_prev:
        if st.session_state[session_state] > 0:
            if st.button("이전", key=f"prev_{session_state}"):
                st.session_state[session_state] -= 1
                st.rerun()

    with col_next:
        if st.session_state[session_state] < pages - 1:
            if st.button("다음", key=f"next_{session_state}"):
                st.session_state[session_state] += 1
                st.rerun()



###
### Phase 1
###
 
st.markdown("""
            <p class="pretendard-bold" style="font-size:24px; margin-bottom:5px">🔥 솔드아웃 아이템</p>
            <p class="pretendard-medium" style="font-size:16px">크림 또는 직구가 아니면 구할 수 없는 아이템들이에요</p>
            """, unsafe_allow_html=True)


# Phase 1-(1)
st.markdown("""<p class="pretendard-semibold" style="font-size:20px">같은 값이면 크림</p>""", unsafe_allow_html=True)
df_tag4 = df.loc[df['tag4_nsprice'] == '1'].reset_index(drop=True)
contents(df_tag4, "phase11")

if st.session_state["id_phase11"]:
    st.markdown("---")

    id_krm = st.session_state["id_phase11"]
    now11 = df_tag4.loc[df_tag4['id_kream'] == id_krm].to_dict(orient="records")[0]

    details_kream(now11)
    details_ns(now11)


st.markdown("---")


# Phase 1-(2)
st.markdown("""<p class="pretendard-semibold" style="font-size:20px">직구로도 구하기 힘들어요</p>""", unsafe_allow_html=True)
df_tag3 = df.loc[(df['tag4_nsprice'] != '1')
                 &(df['tag3_nsstock'] == '1')].reset_index(drop=True)
contents(df_tag3, "phase12")
if st.session_state["id_phase12"]:
    st.markdown("---")

    id_krm = st.session_state["id_phase12"]
    now12 = df_tag3.loc[df_tag3['id_kream'] == id_krm].to_dict(orient="records")[0]

    details_kream(now12)


st.markdown("---")



### 
### Phase 2
### 

st.markdown("""
            <p class="pretendard-bold" style="font-size:24px; margin-bottom:6px">🍦 클래식 아이템</p>
            <p class="pretendard-medium" style="font-size:16px">다른 곳에서도 구할 수 있지만, 크림에서 사는 게 좋은 아이템들이에요</p>
            """, unsafe_allow_html=True)


# Phase 2-(1)
st.markdown("""<p class="pretendard-semibold" style="font-size:20px">크림이 더 싸요</p>""", unsafe_allow_html=True)
df_tag2 = df.loc[(df['tag2_cmcprice'] == '1')].reset_index(drop=True)
contents(df_tag2, "phase21")
if st.session_state["id_phase21"]:
    st.markdown("---")

    id_krm = st.session_state["id_phase21"]
    now21 = df_tag2.loc[df_tag2['id_kream'] == id_krm].to_dict(orient="records")[0]

    details_kream(now21)
    details_mss(now21)


st.markdown("---")


# Phase 2-(2)
st.markdown("""<p class="pretendard-semibold" style="font-size:20px">크림에만 있는 사이즈가 있어요</p>""", unsafe_allow_html=True)
df_tag1 = df.loc[(df['tag2_cmcprice'] != '1') 
                 &(df['tag1_cmcsize'] == '1')].reset_index(drop=True)
contents(df_tag1, "phase22")
if st.session_state["id_phase22"]:
    st.markdown("---")
    
    id_krm = st.session_state["id_phase22"]
    now22 = df_tag1.loc[df_tag1['id_kream'] == id_krm].to_dict(orient="records")[0]

    details_kream(now22)
    details_mss(now22)
    st.markdown("---")
