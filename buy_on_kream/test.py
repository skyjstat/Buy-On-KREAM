import sys
import os

def get_path(relative_path):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
    return os.path.normpath(os.path.join(BASE_DIR, relative_path)) 

pd.DataFrame().to_csv(get_path("../data/test_df.csv"))
