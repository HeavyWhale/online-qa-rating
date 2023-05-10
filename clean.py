import pandas as pd

df = pd.read_excel('asthma.xlsx')

df = df.replace(
    {
        '\n': '',
        '\t': '',
        '\xa0': '',
        '健康咨询描述：': '',
        '^\s+|\s+$': '', # 去掉 leading and trailing whitespaces
    },
    regex=True
)

df.to_csv('asthma_clean.csv', index=False)
