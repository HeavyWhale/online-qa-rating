#!/usr/bin/env python3

import pandas as pd
from functools import reduce

class Print:
    class Color:
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

    def info(s: str, **kwargs) -> None:
        print(f'{Print.Color.BLUE}{s}{Print.Color.END}', **kwargs)

    def warning(s: str, **kwargs) -> None:
        print(f'{Print.Color.YELLOW}{s}{Print.Color.END}', **kwargs)

    def success(s: str, **kwargs) -> None:
        print(f'{Print.Color.GREEN}{s}{Print.Color.END}', **kwargs)

    def error(s: str, **kwargs) -> None:
        print(f'{Print.Color.RED}{s}{Print.Color.END}', **kwargs)
    
    def important(s: str, **kwargs) -> None:
        print(f'{Print.Color.UNDERLINE}{s}{Print.Color.END}', **kwargs)

class WashingMachine:
    in_fun_lookup: dict[str, callable] = {
        'csv':   pd.read_csv,
        'xlsx': pd.read_excel,
        'json':  pd.read_json,
        'sql':   pd.read_sql,
    }
    out_formats: list[str] = [
        'csv', 'excel', 'json', 'sql', 'latex', 'markdown',
    ]

    def __init__(
            self, iftype: str, oftype: str, finalize: bool,
            erase_words: list[str], filter_keywords: list[str]
        ) -> None:
        self.iftype = iftype
        self.oftype = oftype
        self.finalize = finalize
        self.erase_words = erase_words
        self.filter_keywords = filter_keywords
        if iftype not in WashingMachine.in_fun_lookup:
            Print.error(f'> Input file format {iftype} is not supported!')
            exit(1)
        if oftype not in WashingMachine.out_formats:
            Print.error(f'> Output file format {oftype} is not supported!')
            exit(1)

    def clean(self, ifname: str) -> None:
        ifname_no_ext = os.path.splitext(ifname)[0]
        df: pd.DataFrame = self.in_fun_lookup[self.iftype](ifname)
        already_processed = df.columns.size == 18
        answers_num = 3
        target_column_names = \
            ['category', 'is_excluded', 'title','description'] + \
            reduce(
                lambda acc, i: acc + [f'doc{i}', f'hosp{i}', f'pos{i}', f'info{i}', f'ans{i}'],
                range(1, answers_num + 1), []
            )

        def output(suffix: str) -> None:
            fn = {
                'csv':   df.to_csv,
                'excel': df.to_excel,
                'json':  df.to_json,
                'sql':   df.to_sql,
                'latex': df.to_latex,
                'markdown': df.to_markdown
            }[self.oftype]
            if self.finalize and 'FINAL' not in suffix: return
            fn(f'{ifname_no_ext}_{suffix}.{self.oftype}', index=False)
        
        if already_processed:
            Print.warning('> This file has been processed by this program, skipping some steps ...')
            df.columns = ['is_excluded', 'title','description','doc1','hosp1','pos1','info1','ans1','doc2','hosp2','pos2','info2','ans2','doc3','hosp3','pos3','info3','ans3']
        else:
            df.columns = ['title','description','doc1','info1','ans1','doc2','info2','ans2','doc3','info3','ans3']
            df = df.replace(
                { word: '' for word in self.erase_words },
                regex=True
            )
            for i in range(1, answers_num + 1):
                df[[f'doc{i}', f'hosp{i}', f'pos{i}']] = df[f'doc{i}'].str.split(' ', n=2, expand=True)
            df = df[['title','description','doc1','hosp1','pos1','info1','ans1','doc2','hosp2','pos2','info2','ans2','doc3','hosp3','pos3','info3','ans3']]
            df['is_excluded'] = ''
            df = pd.DataFrame(df['is_excluded']).join(df.drop('is_excluded', axis=1))

        # Add category column
        df['category'] = '_'.join(ifname_no_ext.split())
        df = pd.DataFrame(df['category']).join(df.drop('category', axis=1))
        
        assert df.columns.tolist() == target_column_names

        output("replaced")

        base = df.index
        mask = df.apply(
            lambda row: any(keyword in str(row) for keyword in self.filter_keywords),
            axis=1
        )
        df = df[~mask]
        delta_by_keyword = sorted(list(set(base) - set(df.index)))
        Print.info(f'> Filtered indices (by keyword, in total of {len(delta_by_keyword)} rows): ', end='\n\t')
        for (i, index) in enumerate(delta_by_keyword):
            if i > 0 and i % 10 == 0: print(end='\n\t')
            if index == delta_by_keyword[-1]: print(f'#{index}')
            else: print(f'#{index}, ', end='')

        base = df.index
        df = df.drop(df.columns[1], axis=1)
        if not already_processed:
            df = df.dropna()
        delta_by_empty_cell = sorted(list(set(base) - set(df.index)))
        if not already_processed:
            Print.info(f'> Excluded indices (by empty cell, in total of {len(delta_by_empty_cell)} rows): ', end='\n\t')
            for (i, index) in enumerate(delta_by_empty_cell):
                if i > 0 and i % 10 == 0: print(end='\n\t')
                if index == delta_by_empty_cell[-1]: print(f'#{index}')
                else: print(f'#{index}, ', end='')
        Print.info(f'>>> In total of {len(delta_by_keyword) + len(delta_by_empty_cell)} rows are excluded, {len(df)} rows are left <<<')
        output(suffix="excluded")

        df = df.head(100)
        output(suffix='excluded_100')

        fake_data = [
            (39, ['_'.join(ifname_no_ext.split()), '注意力问题','如果您看到此问题，请将所有选项（诊断评分、疾病熟悉程度）选择为4。','','','','','','','','','','','','','','','']),
            (59, ['_'.join(ifname_no_ext.split()), '注意力问题','如果您看到此问题，请将所有选项（诊断评分、疾病熟悉程度）选择为2。','','','','','','','','','','','','','','','']),
            (79, ['_'.join(ifname_no_ext.split()), '注意力问题','如果您看到此问题，请将所有选项（诊断评分、疾病熟悉程度）选择为1。','','','','','','','','','','','','','','','']),
        ]
        indices = [ df.index[i] for (i, _) in fake_data ]
        for (i, (loc, fake_ques)) in enumerate(fake_data):
            df.loc[indices[i]] = fake_ques
        output(suffix='FINAL')
        Print.success(f'> Final file {ifname_no_ext + "_FINAL." + self.oftype} generated, containing first {len(df)} rows')

def main(args):
    if args.clean:
        Print.warning('> Cleaning all generated *.csv and *.xlsx files ...')
        os.system('rm *.csv')
        os.system('rm *_*.xlsx')
        exit(0)

    iftype = args.input_format if args.input_format != 'excel' else 'xlsx'
    oftype = args.output_format
    finalize = args.finalize
    single_file = bool(args.filename)

    erase_words = [
        '\n', '\t', '\xa0', 
        '健康咨询描述：',
        '病情分析：',
        '指导意见：',
        '处理意见：',
        '^\s+|\s+$', # 去掉 leading and trailing whitespaces
    ]
    filter_keywords = [
        '*',
        '图',
        '检查结果',
    ]

    filenames = []
    if args.filename:
        # Processing a single file
        ifname = args.filename
        iftype = os.path.splitext(ifname)[1]
        if not iftype:
            Print.error(f'> Cannot determine input format of file {ifname}')
            exit(1)
        else:
            iftype = iftype[1:]
        filenames.append(ifname)
    else:
        # Processing all files in current working directory
        filenames = list(filter(
            lambda filename: filename.endswith('.xlsx') and '_' not in filename, 
            os.listdir(os.getcwd())
        ))

    Print.warning(f'> Configuration:')
    Print.important(f'\tinput format:', end='')
    Print.info('\t' + iftype)
    Print.important(f'\toutput format:', end='')
    Print.info('\t' + oftype)
    Print.important(f'\tinput file(s):', end='\t')
    if single_file:
        Print.info(args.filename)
    else:
        Print.info('\n\t\tDefaulted to files in current working directory: ')
        Print.info('\t\t' + str(filenames))
    Print.important(f'\tfinalize files:', end='\t')
    Print.info(finalize)
    print()

    if input(f'{Print.Color.YELLOW}> Continue processing [y/n]? {Print.Color.END}') != 'y':
        exit(0)
    print()
    
    wmachine = WashingMachine(
        iftype, oftype, finalize, erase_words, filter_keywords
    )
    for filename in filenames:
        Print.warning(f'> Processing file {filename} ...')
        if filename.startswith('~$'):
            Print.error(f'> File {filename} is a temporary file generated by Excel, skipping ...')
            continue
        # clean(filename, args.output_format, args.final)
        wmachine.clean(filename)
        print()

    if finalize:
        Print.warning('> Concatenating all generated *_FINAL.csv files ...')
        filenames = list(filter(
            lambda filename: 'FINAL' in filename, 
            os.listdir(os.getcwd())
        ))
        dfs: list[pd.DataFrame] = []
        for filename in filenames:
            dfs.append(pd.read_csv(filename))
            os.system(f'rm \'{filename}\'')
        dfs = pd.concat(dfs, ignore_index=True)
        fun =  {
            'csv':   dfs.to_csv,
            'excel': dfs.to_excel,
            'json':  dfs.to_json,
            'sql':   dfs.to_sql,
            'latex': dfs.to_latex,
            'markdown': dfs.to_markdown
        }[oftype]
        fun(f'final.{oftype}', header=False, index=False)
        Print.success(f'> Finished concatenating files into final.{oftype}!')


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
        print(f'{Color.RED}> This file has been processed by this program, skipping some steps ... {Color.END}', end='\n')
        is_processed = True
        df.columns = ['isExcluded', 'title','description','doc1','hosp1','pos1','info1',
                      'ans1','doc2','hosp2','pos2','info2','ans2','doc3',
                      'hosp3','pos3','info3','ans3']
        df['category'] = filename_without_extension
        df = pd.DataFrame(df['category']).join(df.drop('category', axis=1))
    else:
        df.columns = ['title','description','doc1','info1','ans1','doc2','info2','ans2','doc3','info3','ans3']
        erase_words = [
            '\n', '\t', '\xa0', 
            '健康咨询描述：',
            '病情分析：',
            '指导意见：',
            '处理意见：',
            '^\s+|\s+$', # 去掉 leading and trailing whitespaces
        ]
        df = df.replace(
            { keyword: '' for keyword in erase_words },
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
    filter_keywords = sorted(list(set(original) - set(df.index)))
    original = df.index.tolist()
    if is_processed: 
        df = df.drop(df.columns[1], axis=1)
    else:
        df = df.dropna()
    excluded_by_na_cells = sorted(list(set(original) - set(df.index)))
    
    num_exlusions_by_keywords = len(filter_keywords)
    num_exlusions_by_na_cells = len(excluded_by_na_cells)
    print(f'{Color.BLUE}> Excluded indices (by keyword, in total of {num_exlusions_by_keywords} lines): {Color.END}', end='\n\t')
    for (i, index) in enumerate(filter_keywords):
        if i > 0 and i % 10 == 0: print(end='\n\t')
        if index == filter_keywords[-1]: print(f'#{index}')
        else: print(f'#{index}, ', end='')
    if not is_processed:
        print(f'{Color.BLUE}> Excluded indices (by empty cell, in total of {num_exlusions_by_na_cells} lines): {Color.END}', end='\n\t')
        for (i, index) in enumerate(excluded_by_na_cells):
            if i > 0 and i % 10 == 0: print(end='\n\t')
            if index == excluded_by_na_cells[-1]: print(f'#{index}')
            else: print(f'#{index}, ', end='')
    print(f">>> {Color.UNDERLINE}Total of {num_exlusions_by_keywords + num_exlusions_by_na_cells} lines are excluded, {len(df)} lines are left{Color.END} <<<")
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

    parser = argparse.ArgumentParser()
    parser.description = "This program performs clean-up on file(s)"
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
        help="the single file's name (with extension) to be cleaned"
    )
    parser.add_argument(
        "-i", "--input-format",
        choices=["csv", "excel", "json", "sql"],
        default="excel",
        help="the input format of cleaned up file(s), default to excel"
    )
    parser.add_argument(
        "-o", "--output-format",
        choices=["csv", "excel", "json", "sql", "latex", "markdown"],
        default="csv",
        help="the output format of cleaned up file(s), default to csv"
    )
    parser.add_argument(
        "-f", "--finalize",
        action="store_true",
        help="only output the single final concatenated clean file"
    )

    main(parser.parse_args())
