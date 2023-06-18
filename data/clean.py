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
        files = list(filter(lambda f: f.endswith('.xlsx') and f.find('_') == -1, files))

    for file in files:
        print(f'{color.YELLOW}> Processing file {file} ...{color.END}')
        if file.startswith('~$'): 
            print(f'{color.RED}> File {file} is a temporary file generated from Excel, skipping ... {color.END}')
            continue
        clean(file, args.output_format, args.final)
        print()
    
    if args.final:
        print(f'{color.YELLOW}> Combining all generated *_FINAL.csv files ...{color.END}')
        files = list(filter(lambda f: f.find('FINAL') != -1, os.listdir(os.getcwd())))
        dfs = []
        for file in files:
            dfs.append(pd.read_csv(file))
            os.system(f'rm \'{file}\'')
        combined_df = pd.concat(dfs, ignore_index=True)
        fun = combined_df.to_csv if args.output_format == 'csv' else combined_df.to_excel
        fun('final.csv', header=False, index=False)
        print(f'{color.BLUE}> Finished combining!')


def clean(filename: str, format: str, onlyOutputFinalFile: bool):
    filename_without_extension = os.path.splitext(filename)[0]
    def output(suffix: str):
        is_csv = format == "csv"
        fun = df.to_csv if is_csv else df.to_excel
        if onlyOutputFinalFile:
            if "FINAL" in suffix:
                fun(f'{filename_without_extension}_{suffix}.csv', index=False)
        else:
            fun(f'{filename_without_extension}_{suffix}.{"csv" if is_csv else "xlsx"}', index=False)

    df = pd.read_excel(filename)
    is_processed = False
    if df.columns.size == 18:
        print(f'{color.RED}> This file has been processed by this program, skipping some steps ... {color.END}', end='\n')
        is_processed = True
        df.columns = ['isExcluded', 'title','description','doc1','hosp1','pos1','info1',
                      'ans1','doc2','hosp2','pos2','info2','ans2','doc3',
                      'hosp3','pos3','info3','ans3']
        df['category'] = filename_without_extension
        df = pd.DataFrame(df['category']).join(df.drop('category', axis=1))
    else:
        df.columns = ['title','description','doc1','info1','ans1','doc2','info2','ans2','doc3','info3','ans3']
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
        df = df[['title','description','doc1','hosp1','pos1','info1','ans1','doc2','hosp2','pos2','info2','ans2','doc3','hosp3','pos3','info3','ans3']]
        df['category'] = '_'.join(filename_without_extension.split())
        df = pd.DataFrame(df['category']).join(df.drop('category', axis=1))
        output(suffix="replaced")

    exclusion_keywords = [
        '*',
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
    if is_processed: 
        df = df.drop(df.columns[1], axis=1)
    else:
        df = df.dropna()
    excluded_by_na_cells = sorted(list(set(original) - set(df.index)))
    
    num_exlusions_by_keywords = len(excluded_by_keywords)
    num_exlusions_by_na_cells = len(excluded_by_na_cells)
    print(f'{color.BLUE}> Excluded indices (by keyword, in total of {num_exlusions_by_keywords} lines): {color.END}', end='\n\t')
    for (i, index) in enumerate(excluded_by_keywords):
        if i > 0 and i % 10 == 0: print(end='\n\t')
        if index == excluded_by_keywords[-1]: print(f'#{index}')
        else: print(f'#{index}, ', end='')
    if not is_processed:
        print(f'{color.BLUE}> Excluded indices (by empty cell, in total of {num_exlusions_by_na_cells} lines): {color.END}', end='\n\t')
        for (i, index) in enumerate(excluded_by_na_cells):
            if i > 0 and i % 10 == 0: print(end='\n\t')
            if index == excluded_by_na_cells[-1]: print(f'#{index}')
            else: print(f'#{index}, ', end='')
    print(f">>> {color.UNDERLINE}Total of {num_exlusions_by_keywords + num_exlusions_by_na_cells} lines are excluded, {len(df)} lines are left{color.END} <<<")
    output(suffix="excluded")

    df = df.head(100)
    output(suffix="excluded_100")

    fake_data = [
        (39, ['_'.join(filename_without_extension.split()), '注意力问题','如果您看到此问题，请将所有选项（诊断评分、疾病熟悉程度）选择为4。','','','','','','','','','','','','','','','']),
        (59, ['_'.join(filename_without_extension.split()), '注意力问题','如果您看到此问题，请将所有选项（诊断评分、疾病熟悉程度）选择为2。','','','','','','','','','','','','','','','']),
        (79, ['_'.join(filename_without_extension.split()), '注意力问题','如果您看到此问题，请将所有选项（诊断评分、疾病熟悉程度）选择为1。','','','','','','','','','','','','','','','']),
    ]
    indices = [ df.index[i] for (i, _) in fake_data ]
    for (i, (loc, fake_ques)) in enumerate(fake_data):
        df.loc[indices[i]] = fake_ques
    output(suffix='FINAL')

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
    parser.add_argument(
        "-f", "--final",
        action="store_true",
        help="only output the single final clean file"
    )

    main(parser.parse_args())
