from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# 读取Excel文档
data = pd.read_csv('asthma_clean.csv')

@app.route('/')
def index():
    qa = data.iloc[[0]].to_dict(orient='records')[0]
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

    # 将评分追加到Excel文档
    for i, answer in enumerate(answers):
        data.loc[(data['question'] == question), f'score{i+1}'] = scores[i]
    data.to_csv('asthma_result.csv', index=False)

    return 'Scores saved!', 200

if __name__ == '__main__':
    app.run(debug=True)
