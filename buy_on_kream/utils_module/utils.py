import re
import numpy as np

dict_cat_dep = {"신발": "1,37,70,69,55,62,35,71",
            "아우터": "154,161,22,165,169,162,166,158,164,168,157,160,167,156,153,72,159,20,149,150,152,21,163,151,73",
            "상의": "23,74,24,75,195,193,194,196,27,188,26,189,190,191,192,76,77,197,198,199,200,78",
            "하의": "176,177,173,174,178,179,79,175,184,180,181,182,183,80",
            "가방": "19,81,82,84,87,83,86,85,88,89,90",
            "패션잡화": "100,101,102,142,53,105,201,103,104,202,203,106,52,59,107,57,108,109,110,148,111"}

dict_cat= {"신발": "1,37,70,69,55,62,35,71"}

dict_gender = {"남성": "men", "여성": "women"}

dict_size = {'EU 35': '220', '35': '220',
             'EU 35.5': '225',
             'EU 36': '225', '36': '225',
             'EU 36.5': '230',
             'EU 37': '235', '37': '235',
             'EU 37.5': '235',
             'EU 38': '240', '38': '240',
             'EU 38.5': '245',
             'EU 39': '245', '39': '250',
             'EU 39.5': '250',
             'EU 40': '250',
             'EU 40.5': '255',
             'EU 41': '260',
             'EU 41.5': '265',
             'EU 42': '270',
             'EU 42.5': '270',
             'EU 43': '275',
             'EU 43.5': '275',
             'EU 44': '280',
             'EU 44.5': '285',
             'EU 45': '290',
             'EU 45.5': '290',
             'EU 46': '295',
             'EU 46.5': '295',
             'EU 47': '300',
             'EU 47.5': '305',
             'EU 48': '310',
             'EU 48.5': '315',
             'EU 49': '320',
             'EU 49.5': '325',
             'EU 50': '330',
             'UK 3': '220',
             'UK 3.5': '220',
             'UK 4': '225',
             'UK 4.5': '230',
             'UK 5': '235',
             'UK 5.5': '240',
             'UK 6': '245',
             'UK 6.5': '250',
             'UK 7': '255',
             'UK 7.5': '260',
             'UK 8': '265',
             'UK 8.5': '270',
             'UK 9': '275',
             'UK 9.5': '280',
             'UK 10': '285',
             'UK 10.5': '290',
             'UK 11': '295',
             'UK 11.5': '300',
             'UK 12': '305',
             'UK 12.5': '310',
             'UK 13': '315',
             'UK 13.5': '320',
             'UK 14': '325',
             'UK 14.5': '330'
             }


def is_error(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
        return False 
    except Exception:
        return True 


def price_real(type, price):
    if type == "일반배송":
        price_min = round(price * 1.016) + 3000
        price_max = round(price * 1.033) + 3000
    else:
        price_min = round(price * 1.016) + 5000
        price_max = round(price * 1.033) + 5000

    return [price_min, price_max]


# def shoes_size(size, cat):
#     if cat == '신발':
#         size_pattern = r"(?<!\d)(" + "|".join(str(s) for s in range(220, 335, 5)) + r")(?!\d)"
#         match = re.search(size_pattern, size)
#         if match:
#             res = match.group(0)
#         else:
#             size_pattern2 = "|".join(str(s) for s in dict_size.keys())
#             match2 = re.search(size_pattern2, size)
#             if match2:
#                 key = match2.group(0)
#                 res = dict_size[key]
#             else:
#                 res = size
#     else:
#         res = size

#     return res


def shoes_size(size):
    size_pattern = r"(?<!\d)(" + "|".join(str(s) for s in range(220, 335, 5)) + r")(?!\d)"
    match = re.search(size_pattern, size)
    if match:
        res = match.group(0)
    else:
        size_pattern2 = "|".join(str(s) for s in dict_size.keys())
        match2 = re.search(size_pattern2, size)
        if match2:
            key = match2.group(0)
            res = dict_size[key]
        else:
            res = size

    return res


# def make_query(style_code, brand_ko, item_ko):
#     if style_code == '-':
#         res = item_ko.split(' - ')[0]
#     else:
#         res = brand_ko + ' ' + style_code
    
#     return res


brands_except = ['반스']

def make_query(style_code, brand_ko, item_ko):
    if (style_code == '-') or (brand_ko in brands_except):
        res = item_ko.split(' - ')[0]
    else:
        res = brand_ko + ' ' + style_code
    
    return res


def shoes_sizes_near(size, featherL, featherR):
    sizes = [str(s) for s in range(220, 335, 5)]
    index = sizes.index(size)

    start = max(index + featherL, 0)
    end = min(index + featherR + 1, len(sizes))

    return sizes[start:end]


def nearest_sizes(size, featherL, featherR):
    sizes = [str(s) for s in range(220, 335, 5)]
    index = sizes.index(size)

    resultL = sizes[max(0, index + featherL) : index][::-1]  
    resultR = sizes[index + 1 : index + 1 + featherR]  # 오른쪽 확장
    
    result = [size]
    for i in range(max(-featherL, featherR)):
        try:
            result.append(resultR[i])
        except:
            None
        try:
            result.append(resultL[i])
        except:
            None

    return result


def format_price(value):
    if isinstance(value, int):
        return f"{value:,}원"
    elif isinstance(value, str):
        return int(value.replace(',', '').replace('원', ''))
    else:
        return None


def round_price(n):
    return (n // 100) * 100


def kream_v_ns(price_kream, price_ns):
    """
    크림 가격이 대체로 쌀 때
    : 과반수의 크림 가격이 네이버스토어 가격의 중앙값보다 저렴할 때 
    """
    try:
        ref_point = len(price_kream) / 2
    except:
        price_kream = [price_kream]
        ref_point = len(price_kream) / 2
    median = np.median(price_ns)

    list_vs = [1 if p < median else 0 for p in price_kream]
    score_vs = sum(list_vs)
    if score_vs > ref_point:
        res = '1'
    else:
        res = None
    
    return res 


