import os
import pandas as pd

df = pd.DataFrame({
    'a': [1, 2, 3],
    'b': ['x', 'y', 'z']
})

df.to_csv("buy_on_kream/data/test_df.csv", index=False)
