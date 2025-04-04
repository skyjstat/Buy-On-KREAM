from utils_module.utils import is_error, price_real, dict_cat, dict_gender, shoes_size
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver               
from selenium.webdriver.common.by import By  
from datetime import datetime 
import time
import re
import warnings
warnings.filterwarnings('ignore')
from utils_module.utils import make_query, format_price, shoes_size
import os

kream_id = os.environ.get("KREAM_ID")
kream_pw = os.environ.get("KREAM_PW")
