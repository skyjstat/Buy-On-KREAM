import sys
import os
import pandas as pd

def main():
    df = pd.DataFrame({
        'a': [1, 2, 3],
        'b': ['x', 'y', 'z']
    })
    return df

if __name__ == "__main__":
    main()
