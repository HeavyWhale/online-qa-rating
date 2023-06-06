#!/usr/bin/env python3

import pandas as pd

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def main(args):
    if args.clean:
        print(f'{color.YELLOW}> Cleaning all generated *.csv and *.xlsx files ...{color.END}')
        os.system('rm *.csv')
        os.system('rm *_*.xlsx')
        exit(0)

    files = []
    if args.filename:
        filename = args.filename
        if not filename.endswith('.xlsx'): filename += '.xlsx'
        files.append(filename)
    else:
        files = os.listdir(os.getcwd())
        files = list(filter(lambda f: f.endswith('.xlsx'), files))

    for file in files:
        print(f'{color.YELLOW}> Processing file {file} ...{color.END}')
        if file.startswith('~$'): 
            print(f'{color.RED}> File {file} is a temporary file generated from Excel, skipping ... {color.END}')
            continue
        clean(file, args.output_format)
        print()

def clean(filename: str, format: str):
    filename_without_extension = os.path.splitext(filename)[0]
    def output(suffix: str):
        is_csv = format == "csv"
        fun = df.to_csv if is_csv else df.to_excel
        fun(f'{filename_without_extension}_{suffix}.{"csv" if is_csv else "xlsx"}', index=False)

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
    df[['doc1', 'hosp1', 'pos1']] = df['doc1'].str.split(' ', n=2, expand=True)
    df[['doc2', 'hosp2', 'pos2']] = df['doc2'].str.split(' ', n=2, expand=True)
    df[['doc3', 'hosp3', 'pos3']] = df['doc3'].str.split(' ', n=2, expand=True)
    df = df[['title','question','doc1','hosp1','pos1','info1','ans1','doc2','hosp2','pos2','info2','ans2','doc3','hosp3','pos3','info3','ans3']]
    output(suffix="replaced")

    exclusion_keywords = [
        '图',
        '检查结果',
    ]
    original = df.index.tolist()
    mask = df.apply(
        lambda row: any(keyword in str(row) for keyword in exclusion_keywords), 
        axis=1
    )
    df = df[~mask]
    excluded_by_keywords = sorted(list(set(original) - set(df.index)))
    original = df.index.tolist()
    df = df.dropna()
    excluded_by_na_cells = sorted(list(set(original) - set(df.index)))
    
    num_exlusions_by_keywords = len(excluded_by_keywords)
    num_exlusions_by_na_cells = len(excluded_by_na_cells)
    print(f'{color.BLUE}> Excluded indices (by keyword, in total of {num_exlusions_by_keywords} lines): {color.END}', end='\n\t')
    for (i, index) in enumerate(excluded_by_keywords):
        if i > 0 and i % 10 == 0: print(end='\n\t')
        if index == excluded_by_keywords[-1]: print(f'#{index}')
        else: print(f'#{index}, ', end='')
    print(f'{color.BLUE}> Excluded indices (by empty cell, in total of {num_exlusions_by_na_cells} lines): {color.END}', end='\n\t')
    for (i, index) in enumerate(excluded_by_na_cells):
        if i > 0 and i % 10 == 0: print(end='\n\t')
        if index == excluded_by_na_cells[-1]: print(f'#{index}')
        else: print(f'#{index}, ', end='')
    print(f">>> {color.UNDERLINE}Total of {num_exlusions_by_keywords + num_exlusions_by_na_cells} lines are excluded{color.END} <<<")
    output(suffix="excluded")

    df = df.head(100)
    output(suffix="excluded_100")

if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser(
        description="Clean all up *.xlsx file(s) in current directory"
    )
    parser.description = \
        "This program performs clean-ups on all *.xlsx files\
         in current directory if no arguments are provided"
    parser.add_argument(
        "-c", "--clean",
        action="store_true",
        help="clean all generated *.csv and *.xlsx files in current directory"
    )
    parser.add_argument(
        "filename", 
        type=str, 
        nargs="?",
        default=None,
        help="the single *.xlsx file's name (with or without extension) to be cleaned"
    )
    parser.add_argument(
        "-o", "--output-format",
        choices=["csv", "excel"],
        default="csv",
        help="the output format of cleaned up file(s)"
    )

    main(parser.parse_args())
