import os
import pandas as pd

# BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# SAVE_PATH = os.path.join(BASE_DIR, "data/test_df.csv")

print(BASE_DIR)
print(SAVE_PATH)

df = pd.DataFrame({
    'a': [1, 2, 3],
    'b': ['x', 'y', 'z']
})

# df.to_csv(SAVE_PATH, index=False)

df.to_csv("buy_on_kream/data/test_df.csv", index=False)
