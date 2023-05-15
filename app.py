from flask import Flask, render_template, request
import pandas as pd
import os

app = Flask(__name__)

FILE = "./data/diabetes_clean.csv"

# 读取csv文档
data = pd.read_csv(FILE)

i = 0

@app.route('/')
def index():
    global i
    qa = data.iloc[[i]].to_dict(orient='records')[0]
    i += 1
    # qa = data.sample(1).to_dict(orient='records')[0]
    names = [qa['doc1'], qa['doc2'], qa['doc3']]
    infos = [qa['info1'], qa['info2'], qa['info3']]
    answers = [qa['ans1'], qa['ans2'], qa['ans3']]
    template = render_template(
        'index.html',
        title=qa['title'],
        question=qa['question'],
        names=names,
        infos=infos,
        answers=answers
    )
    
    return template

@app.route('/submit', methods=['POST'])
def submit():
    scores = [request.form['score1'], request.form['score2'], request.form['score3']]
    question = request.form['question']
    answers = [request.form['answer1'], request.form['answer2'], request.form['answer3']]

    # 将评分追加到csv文档
    for i, answer in enumerate(answers):
        data.loc[(data['question'] == question), f'score{i+1}'] = scores[i]
    global FILE
    filename = FILE.split('_', 1)[0] + '_result.csv'
    data.to_csv(filename, index=False)

    return render_template('success.html')

if __name__ == '__main__':
    app.run(debug=True)
