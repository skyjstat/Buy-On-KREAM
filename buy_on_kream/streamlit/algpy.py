import pandas as pd
import numpy as np
import re
import warnings
import sys
import os
from utils import shoes_sizes_near, round_price, nearest_sizes, kream_v_ns
pd.set_option('display.max_rows', 10)
warnings.filterwarnings('ignore')

def get_path(relative_path):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
    return os.path.normpath(os.path.join(BASE_DIR, relative_path)) 



def data_prep(gender, size, featherL, featherR):
    df_kream = pd.read_csv(get_path("../data/kream.csv"), index_col=0); df_kream = df_kream.astype({'id_kream': str, 'size_new': str}).rename(columns={'url_img':'img_kream'})
    df_mss = pd.read_csv(get_path("../data/musinsa.csv"), index_col=0); df_mss = df_mss.astype({'id_kream': str, 'id_musinsa': str, 'size_new': str})
    df_ns = pd.read_csv(get_path("../data/ns.csv"), index_col=0); df_ns = df_ns.astype({'id_kream': str})

    df_kream_filtered = df_kream.loc[
        (df_kream['gender'] == gender) & (df_kream['size_new'].isin(shoes_sizes_near(size, featherL, featherR)))
        ].reset_index(drop=True)

    item = df_kream_filtered.drop_duplicates('id_kream')[['id_kream', 'img_kream', 'brand_ko', 'item_ko', 'style_code', 'retail_price']].\
        reset_index(drop=True)
    item['url_kream'] = 'https://kream.co.kr/products/' + item['id_kream']

    df_mss_filtered = df_mss.loc[(df_mss['id_kream'].isin(item['id_kream'])) & (df_mss['size_new'].isin(shoes_sizes_near(size, featherL, featherR)))].reset_index(drop=True)

    info = item[['id_kream']]

    # 크림 
    df_kream_filtered['kream'] = df_kream_filtered.\
        apply(lambda row: {row['size_new']: {'price_min': row['price_min'], 'price_max': row['price_max']}}, axis=1)
    key_kream = df_kream_filtered.groupby('id_kream')['kream'].apply(list).reset_index()

    # 네이버 스토어 
    df_ns['id_ns'] = df_ns['href'].str.split('/').str[-1].str.split('?').str[0]
    df_ns['ns'] = df_ns.apply(lambda row: {'id_ns': row['id_ns'], 'item': row['item'], 'price': row['price'], 'url': row['href'], 'img': row['url_img']}, axis=1)
    key_ns = df_ns.groupby('id_kream')['ns'].apply(list).reset_index()

    # 무신사 
    key_mss_size = df_mss_filtered.groupby('id_musinsa')['size_new'].apply(list).reset_index()
    df_mss_filtered = pd.merge(df_mss_filtered, key_mss_size, on='id_musinsa', how='left')
    df_mss_filtered['mss'] = df_mss_filtered.apply(lambda row: {'id_musinsa': row['id_musinsa'], 'size': row['size_new_y'], 'price': row['price'], 'url': 'https://www.musinsa.com/products/' + str(row['id_musinsa']), 'img': row['url_img']},
        axis=1)
    key_mss = df_mss_filtered.drop_duplicates('id_kream')[['id_kream', 'mss']].reset_index(drop=True)

    for key in [key_kream, key_mss, key_ns]:
        info = pd.merge(info, key, on='id_kream', how='left')

    return item, info


def tag_rows(item, info, size, featherL, featherR):
    ### 무신사 매물 X
    # (1) 품목 없음 
    info.loc[info['mss'].isna(), 'tag0_cmcstock'] = '1'

    # (2) 품목 있음, 사이즈 없음
    tmp = info.loc[~info['mss'].isna()]
    tmp['size_kream'] = tmp.apply(lambda row: [list(d.keys())[0] for d in row['kream']], axis=1)
    tmp['size_mss'] = tmp.apply(lambda row: row['mss']['size'], axis=1)
    tmp['size_only_kream'] = tmp.apply(lambda row: list(set(row['size_kream']).difference(set(row['size_mss']))), axis=1)

    tag1_index = tmp.loc[tmp['size_only_kream'].apply(lambda x: len(x) != 0)].index
    info.loc[tag1_index, 'tag1_cmcsize'] = '1'


    ### 무신사 매물 O
    tmp2 = info.loc[info['tag0_cmcstock'].isna()]
    tmp2['price_mss'] = tmp2['mss'].apply(lambda x: round(x['price']*0.85))
    tmp2['price_kream'] = tmp2['kream'].apply(lambda x: [list(d.values())[0]['price_max'] for d in x])
    # tmp2['price_kream'] = tmp2['kream'].apply(lambda x: {list(d.keys())[0]: list(d.values())[0]['price_max'] for d in x})

    tag2_index = tmp2[tmp2.apply(lambda row: any(x < row['price_mss'] for x in row['price_kream']), axis=1)].index
    info.loc[tag2_index, 'tag2_cmcprice'] = '1'


    ### 네이버스토어 매물 X
    info.loc[((info['tag0_cmcstock'] == '1') | (info['tag2_cmcprice'] == '1')) & (info['ns'].isna()), 'tag3_nsstock'] = '1'


    ### 네이버스토어 매물 X, 가격 비교 
    tmp3 = info.loc[((info['tag0_cmcstock'] == '1') | (info['tag2_cmcprice'] == '1')) & (info['tag3_nsstock'].isna())]
    tmp3['price_kream'] = tmp3['kream'].apply(lambda x: [list(d.values())[0]['price_max'] for d in x])
    tmp3['price_ns'] = tmp3['ns'].apply(lambda x: [d['price'] for d in x])

    tmp3['tag4_nsprice'] = tmp3.apply(lambda row: kream_v_ns(row['price_kream'], row['price_ns']), axis=1)
    tag4_index = tmp3.loc[tmp3['tag4_nsprice'] == '1'].index
    info.loc[tag4_index, 'tag4_nsprice'] = '1'

    df = pd.merge(item, info, on='id_kream', how='left')

    df['kream_rep_price'] = df['kream'].apply(lambda x: next(
        (d[key]['price_max'] for key in nearest_sizes(size, featherL, featherR) for d in x if key in d),
    ))
    
    df['kream_rep_size'] = df['kream'].apply(lambda x: next(
        (key for key in nearest_sizes(size, featherL, featherR) for d in x if key in d),
    ))

    df.to_csv(get_path('../final/df_main.csv'))

    return df
