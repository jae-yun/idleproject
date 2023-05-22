from flask import Flask, render_template, request, send_from_directory
import os

app = Flask(__name__)

# 메인 화면
@app.route('/')
def index():
    return render_template('index.html'), 200

# 예측 메인 화면
@app.route('/costpredict', methods = ['GET'])
def costpredict():
    return render_template('costpredict.html'), 200

# favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, ''), 'favicon.ico')

# 예측 결과 화면
@app.route('/costpredict/result', methods=['POST'])
def costpredict_result():
    if request.method == 'POST':
        # date : YYYY-MM-DD 형식으로 받아옴
        date = request.form['date']
        # destination : HND or NRT
        destination = request.form['destination']
        return render_template('result_cost.html', date=date, destination=destination), 200

# 추천 메인 화면
@app.route('/recommend', methods=['GET'])
def recommend():
    return render_template('recommend.html'), 200

# 추천 결과 화면
@app.route('/recommend/result', methods=['POST'])
def recommend_result():
    if request.method == 'POST':
        # date : YYYY-MM-DD 형식으로 받아옴
        date = request.form['date']
        # destination : HND or NRT
        destination = request.form['destination']
        # cost : 500000
        cost = request.form['cost']
        return render_template('result_reco.html', date=date, destination=destination, cost=cost), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9900)
