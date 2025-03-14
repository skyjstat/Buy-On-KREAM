import streamlit as st
from utils_streamlit import load_fonts, process_image, format_round_price, format_title

load_fonts()


def details_kream(nowD):
    colL, colR = st.columns([2, 3])
    colL.image(process_image(nowD['img_kream'], background_color=(240, 240, 240)))

    with colR:
        st.markdown(
            f"""
            <p class="pretendard-semibold" style="font-size:20px; margin-bottom:6px; margin-top:0px">{nowD['item_ko']}</p>
            <p style="margin-top:0px; margin-bottom:0px">
                <span class="pretendard-semibold">발매가 </span>
                <span class="pretendard-medium">{nowD['retail_price']} | </span>
                <span class="pretendard-semibold">모델번호 </span>
                <span class="pretendard-medium">{nowD['style_code']}</span>
            </p>
            """,
            unsafe_allow_html=True
        )

        kream = nowD['kream']
        st.markdown("---")

        st.markdown(f"""
                    <p style="margin-bottom:3px">
                        <span class="pretendard-bold" style="font-size:18px; margin-top:0px;">KREAM 예상가</span>
                        <span style="font-size:3px">ㅤ</span>
                        <span>
                            <a href="{nowD['url_kream']}" target="_blank">
                                <button class="pretendard-medium" 
                                style="color:gray; font-size:14px; cursor:pointer; border-radius:5px; background-color:#f2f2f2; padding:2px 8px 2px 8px; border:0px">
                                이동
                                </button>
                            </a>                            
                        </span>
                    </p>
                    <p class="pretendard-medium" style="font-size:16px">3.3%의 예상 수수료가 포함된 가격이에요</p>
                    """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for r in range(2):
            for i, c in enumerate(cols):
                with c:
                    try:
                        item = kream[(3*r+i)]
                        size = list(item.keys())[0]; price = list(item.values())[0]['price_max']
                        st.markdown(f"""
                                    <p style="margin-top:0px; margin-bottom:6px">
                                        <span class="pretendard-medium" style="font-size:13px; color:gray; background-color:#FFE7F2; padding:3px 4px 3px 8px; border-radius:5px;">
                                            {size}
                                        </span>
                                        <span style="font-size:3px">ㅤ</span>
                                        <span class="pretendard-semibold" style="font-size:14px;">{format_round_price(price)}</span>
                                    </p>
                                    """, unsafe_allow_html=True)
                    except:
                        st.write("")


def details_ns(nowD):
    ns = nowD['ns']
    if isinstance(ns, float):
        st.write("")
    else:
        st.markdown("---")
        st.markdown("""
                    <p class="pretendard-bold" style="font-size:20px; margin-bottom:3px">네이버 스토어</p>
                    <p class="pretendard-medium" style="font-size:16px; margin-bottom:28px">배송비가 포함된 가격이에요. 정확한 사이즈, 색상 여부는 확인이 필요해요</p>
                    """, unsafe_allow_html=True)

        cols = st.columns(5)
        for r in range(2):
            for i, c in enumerate(cols):
                with c:
                    item = ns[(5*r+i)]
                    st.image(process_image(item['img']))
                    st.markdown(f"""
                                <p>
                                    <span class="pretendard-semibold" style="font-size:14px;">{format_round_price(item['price'])}</span>
                                    <span style="font-size:3px">ㅤ</span>
                                    <span>
                                        <a href="{item['url']}" target="_blank">
                                            <button class="pretendard-medium" 
                                            style="color:gray; font-size:13px; cursor:pointer; border-radius:5px; background-color:#f2f2f2; padding:2px 7px 0px 6.5px; border:0px">
                                            이동
                                            </button>
                                        </a>                            
                                    </span>
                                </p>
                                """, unsafe_allow_html=True)

def details_mss(nowD):
    mss = nowD['mss']
    if isinstance(mss, float):
        st.write("")
    else:
        st.markdown("---")

        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
                        <p style="margin-bottom:3px">
                            <span class="pretendard-bold" style="font-size:20px;">MUSINSA</span>
                            <span style="font-size:3px">ㅤ</span>
                            <span>
                                <a href="{mss['url']}" target="_blank">
                                    <button class="pretendard-medium" 
                                    style="color:gray; font-size:14px; cursor:pointer; border-radius:5px; background-color:#f2f2f2; padding:2px 8px 2px 8px; border:0px">
                                    이동
                                    </button>
                                </a>                            
                            </span>
                        </p>
                        <p class="pretendard-medium" style="font-size:16px; margin-top:0px">사이즈 재고 현황이 반영되었어요</p>
                        """, unsafe_allow_html=True)

            size_mss = f"""<p><span class="pretendard-semibold style="font-size:14px">{format_round_price(mss["price"])}</span><span style="font-size:10px">ㅤ</span>"""
            for s in mss['size']:
                size_mss += f"""<span class="pretendard-medium" style="font-size:13px; color:gray; background-color:#FFE7F2; padding:3px 8px 3px 8px; border-radius:5px;">{s}</span><span style="font-size:3px">ㅤ</span>"""
            size_mss += """</p>"""

            st.markdown(size_mss, unsafe_allow_html=True)

        col2.image(process_image(mss["img"], crop=True))
