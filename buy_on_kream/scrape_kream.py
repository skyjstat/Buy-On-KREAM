from utils_module.utils import is_error, price_real, dict_cat, dict_gender, shoes_size
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver               
from selenium.webdriver.common.by import By  
from selenium.webdriver.chrome.options import Options
from datetime import datetime 
import time
import re
import warnings
warnings.filterwarnings('ignore')
from utils_module.utils import make_query, format_price, shoes_size
import os

kream_id = os.environ.get("KREAM_ID")
kream_pw = os.environ.get("KREAM_PW")


def scrape_kream(driver, kream_id, kream_pw):
    """ LOGIN """
    url_login = 'https://kream.co.kr/login'
    driver.get(url_login)
    time.sleep(1)
    print("### 로그인 페이지 이동 완료 ###")

    driver.find_elements(By.CLASS_NAME, 'input_txt')[0].send_keys(kream_id)
    driver.find_elements(By.CLASS_NAME, 'input_txt')[1].send_keys(kream_pw)
    time.sleep(0.3)

    driver.find_element(By.CLASS_NAME, 'login-btn-box').find_element(By.CLASS_NAME, 'btn.full.solid').click()

  
    """ ITEM """
    item_df = pd.DataFrame()

    for cat in dict_cat.keys():
        for gender in dict_gender.keys():
            url_shop = f'https://kream.co.kr/search?stockout_invisible=true&sort=popular_score&gender={dict_gender[gender]}&shop_category_id={dict_cat[cat]}' 
            driver.get(url_shop)
            time.sleep(1)

            # 페이지 스크롤
            for i in range(5): # 300개 기준 
                last_no = 49 + i*50
                # print('Scroll down trial :', i+1)
                last_element = driver.find_element(By.CSS_SELECTOR, f"div[data-result-index='{last_no}']") 
                height = last_element.location['y']

                while True:
                    driver.execute_script(f"window.scrollTo(0, {height})")
                    time.sleep(1.5)

                    val = is_error(driver.find_element, By.CSS_SELECTOR, f"div[data-result-index='{last_no + 50}']")
                    if val == False:
                        break

                    height += 10

            soup = BeautifulSoup(driver.page_source)
            raw = soup.find('div', attrs={'class':'search_result_list'}).find_all('a')
            url_item = ['https://kream.co.kr' + r.get('href') for r in raw]
            url_img = [r.find("picture").find("source").get("srcset") for r in raw]

            tmp = pd.DataFrame({'category': [cat] * len(url_item), 'gender': [gender] * len(url_item), 'url_item': url_item, 'url_img': url_img}) 
            item_df = pd.concat([item_df, tmp], axis=0).reset_index(drop=True)

    item_df['id_kream'] = item_df['url_item'].str.split('/').str[-1]


    """ DETAILS """
    item_df_unq = item_df.drop_duplicates('id_kream').reset_index(drop=True)

    kream_df = pd.DataFrame()

    for i in range(len(item_df_unq)):
        now = item_df_unq.loc[i]
        url_item = now['url_item']
        id_kream = now['id_kream']

        driver.get(url_item)
        time.sleep(0.3)
        
        print(i)
        soup = BeautifulSoup(driver.page_source)

        try:
            # 기본정보 : 브랜드명, 상품명, 모델번호
            brand_en = soup.select_one("div.brand-shortcut p.text-lookup.title-text").get_text()
            brand_ko = soup.select_one("div.brand-shortcut p.text-lookup.subtitle").get_text()
            item_en = soup.find("p", class_="title").get_text().strip()
            item_ko = soup.find("p", class_="sub-title").get_text()
            style_code = soup.select_one("div.detail-box.model_number div.product_info").get_text().strip().split('/')[-1]
            retail_price = soup.select_one("div:has(> .product_title:contains('발매가')) > .product_info").get_text().strip()
            color = list(set(soup.find("div", class_="product_info color-target").get_text().strip().split('/')))

            main_info = [id_kream, brand_en, brand_ko, item_en, item_ko, style_code, retail_price, color]

            # 상세정보 : 사이즈, 배송유형, 가격 
            button_buy = driver.find_element(By.XPATH, "//button[strong[text()='구매']]")
            button_buy.click()
            time.sleep(0.2)

            buttons_size = driver.find_elements(By.CLASS_NAME, "select_item")
            detail_tmp = pd.DataFrame() 

            for button_size in buttons_size:
                try:
                    button_size.click()
                except:
                    scrollable_div = driver.find_element(By.CLASS_NAME, "layer-detail-size-select-content")
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", scrollable_div)
                    button_size.click()
                time.sleep(0.05)
                soup = BeautifulSoup(driver.page_source)

                # 사이즈 
                size = soup.find("div", class_=lambda x: x and x.startswith("select_item") and x.endswith("selected")).find('p').get_text()

                # 배송유형, 가격
                raw = soup.select_one("div.bottomsheet__content div.layout_list_vertical").find_all("div", class_="select_option_picker")
                type0 = [r.find("div", class_="justified__text").find("p").get_text() for r in raw]
                type1 = [r.get_text() if r != None else r for r in [r.find("div", class_="tag_element") for r in raw]]
                type = [b if b != None else a for a, b in zip(type0, type1)]
                price = ["".join(filter(str.isdigit, p)) for p in [r.find("div", class_="justified__description").find("p").get_text() for r in raw]]

                if type == [] and price == []:
                    type = ['']
                    price = ['']

                option_tmp = pd.DataFrame({'size': [size] * len(type), 'type': type, 'price': price})
                detail_tmp = pd.concat([detail_tmp, option_tmp], axis=0).reset_index(drop=True)
            
            main_tmp = pd.DataFrame([main_info] * len(detail_tmp), columns = ['id_kream', 'brand_en', 'brand_ko', 'item_en', 'item_ko', 'style_code', 'retail_price', 'color'])
            
            kream_tmp = pd.concat([main_tmp, detail_tmp], axis=1)
            kream_df = pd.concat([kream_df, kream_tmp], axis=0).reset_index(drop=True)
        except:
            continue

    return item_df, kream_df


def post_processing(item_df, kream_df):  
    """ POST-PROCESSING """
    kream_df_merged = pd.merge(item_df[['category', 'gender', 'id_kream', 'url_img']], kream_df, on='id_kream', how='left').dropna().reset_index(drop=True)

    kream_df_merged = kream_df_merged.loc[(kream_df_merged['type'] != '95점') & (kream_df_merged['type'] != '') & (kream_df_merged['price'] != '')].reset_index(drop=True)
    kream_df_merged['size_new'] = kream_df_merged.apply(lambda row: shoes_size(row['size'], row['category']), axis=1)
    kream_df_merged['price'] = kream_df_merged['price'].astype(int)
    kream_df_merged['item_en'] = kream_df_merged['item_en'].str.strip()

    kream_df_merged = kream_df_merged.loc[kream_df_merged.groupby(['style_code', 'size'])['price'].idxmin()].sort_index().reset_index(drop=True)
    kream_df_merged[['price_min', 'price_max']] = kream_df_merged.apply(lambda row: price_real(row['type'], row['price']), axis=1).apply(pd.Series)

    return kream_df_merged


def main():
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')


    driver = webdriver.Chrome(options=options); print("### 웹드라이버 생성 완료 ###")
    # driver = webdriver.Chrome()
    item_df, kream_df = scrape_kream(driver, kream_id, kream_pw)
    driver.quit()

    kream_df_merged = post_processing(item_df, kream_df)
    kream_df_merged.to_csv("buy_on_kream/data/kream.csv")


if __name__ == "__main__":
    main()
