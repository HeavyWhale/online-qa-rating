#!/usr/bin/env python3

import pandas as pd
from functools import reduce
from pprint import pformat

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
        'excel': pd.read_excel,
        'json':  pd.read_json,
        'sql':   pd.read_sql,
    }
    fext_lookup: dict[str, str] = {
        'csv': 'csv',
        'excel': 'xlsx',
        'json': 'json',
        'sql': 'sql',
        'latex': 'tex',
        'markdown': 'md',
    }
    out_formats: list[str] = [
        'csv', 'excel', 'json', 'latex', 'markdown',
    ]

    def __init__(
            self, iftype: str, oftype: str, finalize: bool, single_file: bool,
            erase_words: list[str], filter_keywords: list[str]
        ) -> None:
        self.iftype = iftype
        self.oftype = oftype
        self.finalize = finalize
        self.single_file = single_file
        self.erase_words = erase_words
        self.filter_keywords = filter_keywords

        self.ifext = WashingMachine.fext_lookup[iftype]
        self.ofext = WashingMachine.fext_lookup[oftype]

        if iftype not in WashingMachine.in_fun_lookup:
            Print.error(f'> Input file format {iftype} is not supported!')
            exit(1)
        self.infun = self.in_fun_lookup[self.iftype]
        if oftype not in WashingMachine.out_formats:
            Print.error(f'> Output file format {oftype} is not supported!')
            exit(1)

    def clean(self, ifname: str) -> pd.DataFrame:
        ifname_no_ext = os.path.splitext(ifname)[0]
        df: pd.DataFrame = self.infun(ifname)
        already_processed = df.columns.size == 18
        answers_num = 3
        target_column_names = \
            ['category', 'is_excluded', 'title','description'] + \
            reduce(
                lambda acc, i: acc + [f'doc{i}', f'hosp{i}', f'pos{i}', f'info{i}', f'ans{i}'],
                range(1, answers_num + 1), []
            )

        def output(suffix: str) -> str:
            fn = {
                'csv':   df.to_csv,
                'excel': df.to_excel,
                'json':  df.to_json,
                'latex': df.to_latex,
                'markdown': df.to_markdown
            }[self.oftype]
            if self.single_file or (self.finalize and 'FINAL' not in suffix): return
            ofname = f'{ifname_no_ext}_{suffix}[gen].{self.ofext}'
            fn(ofname, index=False)
            return ofname
        
        if already_processed:
            Print.warning('> This file has been processed by this program, skipping some steps ...')
            df.columns = ['is_excluded', 'title','description','doc1','hosp1','pos1','info1','ans1','doc2','hosp2','pos2','info2','ans2','doc3','hosp3','pos3','info3','ans3']
        else:
            df.columns = ['title','description','doc1','info1','ans1','doc2','info2','ans2','doc3','info3','ans3']
            # Earse appearance(s) of word(s) from earse_words
            df = df.replace(
                { word: '' for word in self.erase_words },
                regex=True
            )
            # Split doc's name, hospital, and position from `doc` column
            for i in range(1, answers_num + 1):
                df[[f'doc{i}', f'hosp{i}', f'pos{i}']] = df[f'doc{i}'].str.split(' ', n=2, expand=True)
            df = df[['title','description','doc1','hosp1','pos1','info1','ans1','doc2','hosp2','pos2','info2','ans2','doc3','hosp3','pos3','info3','ans3']]
            # Enable manual modification by adding `is_excluded` column
            df['is_excluded'] = ''
            df = pd.DataFrame(df['is_excluded']).join(df.drop('is_excluded', axis=1))

        # Add category column
        df['category'] = '_'.join(ifname_no_ext.split())
        df = pd.DataFrame(df['category']).join(df.drop('category', axis=1))
        
        assert df.columns.tolist() == target_column_names
        output("replaced")

        # Filter rows by keyword(s) from filter_keywords
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

        # Filter rows by empty cells
        base = df.index
        df = df.drop(df.columns[1], axis=1) # drop `is_excluded` column
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
        output(suffix='100')

        fake_data = [
            (39, ['_'.join(ifname_no_ext.split()), '注意力问题','如果您看到此问题，请将所有选项（诊断评分、疾病熟悉程度）选择为4。','','','','','','','','','','','','','','','']),
            (59, ['_'.join(ifname_no_ext.split()), '注意力问题','如果您看到此问题，请将所有选项（诊断评分、疾病熟悉程度）选择为2。','','','','','','','','','','','','','','','']),
            (79, ['_'.join(ifname_no_ext.split()), '注意力问题','如果您看到此问题，请将所有选项（诊断评分、疾病熟悉程度）选择为1。','','','','','','','','','','','','','','','']),
        ]
        for (i, (loc, fake_ques)) in enumerate(fake_data):
            # insert the fake question at index i into df
            new_row = pd.DataFrame([fake_ques], columns=df.columns)
            df = pd.concat([df.iloc[:loc], new_row, df.iloc[loc:]]).reset_index(drop=True)
        suffix = 'FINAL' if self.finalize else 'fake'
        ofname = output(suffix)
        if not self.single_file:
            Print.success(f'> Final file {ofname} generated, containing first {len(df)} rows')

        return df

def main(args):
    if args.clean:
        Print.warning('> Cleaning all generated files in current directory ...')
        os.system('rm -v *\[gen\].*')
        os.system('rm -v final.*')
        exit(0)

    iftype = args.input_format
    ifext = WashingMachine.fext_lookup[iftype]
    oftype = args.output_format
    ofext = WashingMachine.fext_lookup[oftype]
    finalize = args.finalize
    file_from_input = bool(args.filename)
    single_file = args.single_file

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
        ifext = os.path.splitext(ifname)[1]
        if not ifext:
            Print.error(f'> Cannot determine input format of file {ifname}')
            exit(1)
        else:
            ifext = ifext[1:]
        filenames.append(ifname)
    else:
        # Processing all files in current directory
        filenames = list(filter(
            lambda filename: filename.endswith(f'.{ifext}') and '_' not in filename, 
            os.listdir(os.getcwd())
        ))

    Print.warning(f'> Configurations:')
    Print.important(f'\tInput file extsion:', end='')
    Print.info('\t.' + ifext)
    Print.important(f'\tOutput file extsion:', end='')
    Print.info('\t.' + ofext)
    Print.important(f'\tInput filename(s):', end='\t')
    if file_from_input:
        Print.info(args.filename)
    else:
        Print.info('\n\t\tDefaulted to files in current directory: ')
        fstr = pformat(filenames, indent=2, compact=True).replace('\n','\n\t\t')
        Print.info('\t\t' + fstr)
    Print.important(f'\tFinalize files?:', end='\t')
    Print.info(finalize)
    Print.important(f'\tOutput single file?:', end='\t')
    Print.info(single_file)
    print()

    if input(f'{Print.Color.YELLOW}> Continue processing [y/n]? {Print.Color.END}') != 'y':
        exit(0)
    print()
    
    washing_machine = WashingMachine(
        iftype, oftype, finalize, single_file, erase_words, filter_keywords
    )
    dfs: list[pd.DataFrame] = []
    for filename in filenames:
        Print.warning(f'> Processing file {filename} ...')
        if filename.startswith('~$'):
            Print.error(f'> File {filename} is a temporary file generated by Excel, skipping ...')
            continue
        dfs.append(washing_machine.clean(filename))
        print()

    if single_file:
        dfs: pd.DataFrame = pd.concat(dfs, ignore_index=True)
        ofun =  {
            'csv':   dfs.to_csv,
            'excel': dfs.to_excel,
            'json':  dfs.to_json,
            'latex': dfs.to_latex,
            'markdown': dfs.to_markdown,
        }[oftype]
        if oftype in ['markdown']:
            ofun(f'final.{ofext}', index=False)
        else:
            ofun(f'final.{ofext}', header=False, index=False)
        Print.success(f'> Generated final file final.{ofext}!')

if __name__ == '__main__':
    import os
    import argparse

    parser = argparse.ArgumentParser()
    parser.description = "This program performs clean-up on file(s)"
    parser.add_argument(
        "-c", "--clean",
        action="store_true",
        help="clean all generated files in current directory"
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
        choices=["csv", "excel", "json", "latex", "markdown"],
        default="csv",
        help="the output format of cleaned up file(s), default to csv"
    )
    parser.add_argument(
        "-f", "--finalize",
        action="store_true",
        help="only output the final clean file for each input file"
    )

    parser.add_argument(
        "-s", "--single-file",
        action="store_true",
        help="only output the single final clean concatenated file"
    )

    parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help='automatic yes to prompts; assume "yes" as answer to all prompts and run non-interactively.'
    )

    main(parser.parse_args())
