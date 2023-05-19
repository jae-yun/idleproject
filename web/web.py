from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 메인 화면
@app.route('/')
def index():
    return render_template('index.html'), 200

# 예측 메인 화면
@app.route('/costpredict', methods = ['GET'])
def costpredict():
    return render_template('costpredict.html')

# 예측 결과 화면
@app.route('/costpredict/result', methods=['POST'])
def costpredict_result():
    if request.method == 'POST':
        # date : YYYY-MM-DD 형식으로 받아옴
        date = request.form['date']
        # destination : HND or NRT
        destination = request.form['destination']
        return render_template('index.html', date=date, destination=destination)

# 추천 메인 화면
@app.route('/recommend', methods=['GET'])
def recommend():
    return render_template('recommend.html')

# 추천 결과 화면
@app.route('/recommend/result', methods=['POST'])
def recommend_result():
    if request.method == 'POST':
        # date : YYYY-MM-DD 형식으로 받아옴
        date = request.form['date']
        # destination : HND or NRT
        destination = request.form['destination']
        # int 형식으로 비용 받아옴.
        cost = int(request.form['cost'])
        return render_template('index.html', date=date, destination=destination, cost=cost)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9900)
