import pandas as pd
import os

def clean(filename: str):
    df = pd.read_excel(filename)
    df = df.replace(
        {
            '\n': '',
            '\t': '',
            '\xa0': '',
            '健康咨询描述：': '',
            '病情分析：': '',
            '指导意见：': '',
            '处理意见：': '',
            '^\s+|\s+$': '', # 去掉 leading and trailing whitespaces
        },
        regex=True
    )
    filename_without_extension = os.path.splitext(filename)[0]
    df.to_csv(f'{filename_without_extension}.csv', index=False)

if __name__ == '__main__':
    files = os.listdir(os.getcwd())
    files = list(filter(lambda f: f.endswith('.xlsx'), files))
    for file in files:
        clean(file)
