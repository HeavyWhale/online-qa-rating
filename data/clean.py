import pandas as pd
import os
import sys

def clean(filename: str):
    df = pd.read_excel(filename)

    df.columns = ['title','question','doc1','info1','ans1','doc2','info2','ans2','doc3','info3','ans3']

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
    deleted_indices_exclusion_keywords = sorted(list(set(original_indices) - set(df.index)))
    
    original_indices = df.index.tolist()
    df = df.dropna()
    deleted_indices_na_cells = sorted(list(set(original_indices) - set(df.index)))
    
    print('Deleted indices (exclusion keyword): ', end='')
    for index in deleted_indices_exclusion_keywords:
        if index == deleted_indices_exclusion_keywords[-1]:
            print(f'#{index}')
        else:
            print(f'#{index}, ', end='')

    print('Deleted indices (empty cell): ', end='')
    for index in deleted_indices_na_cells:
        if index == deleted_indices_na_cells[-1]:
            print(f'#{index}')
        else:
            print(f'#{index}, ', end='')

    df.to_csv(f'{filename_without_extension}_clean.csv', index=False)

if __name__ == '__main__':
    files = []

    if len(sys.argv) <= 1:
        files = os.listdir(os.getcwd())
        files = list(filter(lambda f: f.endswith('.xlsx'), files))
    else:
        arg = ''.join(sys.argv[1])
        if arg == 'clean':
            print(f'> Cleaning all *.csv files ...')
            os.system('rm *.csv')
            exit(0)
        if not arg.endswith('.xlsx'): arg += '.xlsx'
        files.append(arg)

    for file in files:
        print(f'> Processing file {file} ...')
        clean(file)
        print()
