import pandas as pd
import os

def clean(filename: str):
    df = pd.read_excel(filename)

    replace_keywords = [
        '\n', '\t', '\xa0', 
        '健康咨询描述：',
        '病情分析：',
        '指导意见：',
        '处理意见：',
        '^\s+|\s+$', # 去掉 leading and trailing whitespaces
    ]
    df = df.replace(
        { keyword: '' for keyword in replace_keywords },
        regex=True
    )
    filename_without_extension = os.path.splitext(filename)[0]
    df.to_csv(f'{filename_without_extension}.csv', index=False)

    exclusion_keywords = [
        '图',
        '检查结果',
    ]
    original_indices = df.index.tolist()
    mask = df.apply(
        lambda row: any(keyword in str(row) for keyword in exclusion_keywords), 
        axis=1
    )
    df = df[~mask]
    deleted_indices = sorted(list(set(original_indices) - set(df.index)))
    print('Deleted indices: ', end='')
    for index in deleted_indices:
        if index == deleted_indices[-1]:
            print(f'#{index}')
        else:
            print(f'#{index}, ', end='')

    df.to_csv(f'{filename_without_extension}_clean.csv', index=False)

if __name__ == '__main__':
    files = os.listdir(os.getcwd())
    files = list(filter(lambda f: f.endswith('.xlsx'), files))
    for file in files:
        print(f'> Processing file {file} ...')
        clean(file)
        print()
