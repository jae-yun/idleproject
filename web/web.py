from flask import Flask, render_template, request
from src.data_matcher import model, pred_by_ml
import pandas as pd

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
def result_cost():
    if request.method == 'POST':
        destination = request.form['destination']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        input_start_date = int(start_date.split('-')[1]) * 100 + int(start_date.split('-')[2])
        input_end_date = int(end_date.split('-')[1]) * 100 + int(end_date.split('-')[2])


        plain1, plain2, res1, res2, res3, trans_total, total1, total2, total3 = pred_by_ml(input_start_date,
                                                                                           input_end_date,
                                                                                           destination)

        print(plain1, plain2, res1, res2, res3, trans_total, total1, total2, total3)

        total_cost_lower_bound = int(total1)
        total_cost_upper_bound = int(total2)
        departure_ticket_cost = int(plain1)
        return_ticket_cost = int(plain2)
        accommodation_cost_lower_bound = res1
        accommodation_cost_upper_bound = res2
        average_transportation_cost = trans_total

        print(destination, start_date, end_date)
        return render_template('result_cost.html',
                               destination=destination,
                               start_date=start_date,
                               end_date=end_date,
                               total_cost_lower_bound=total_cost_lower_bound,
                               total_cost_upper_bound=total_cost_upper_bound,
                               departure_ticket_cost=departure_ticket_cost,
                               return_ticket_cost=return_ticket_cost,
                               accommodation_cost_lower_bound=accommodation_cost_lower_bound,
                               accommodation_cost_upper_bound=accommodation_cost_upper_bound,
                               average_transportation_cost=average_transportation_cost
                               )


# 추천 메인 화면
@app.route('/recommend', methods=['GET'])
def recommend():
    return render_template('recommend.html')

# 추천 결과 화면
@app.route('/recommend/result', methods=['POST'])
def result_reco():
    if request.method == 'POST':
        # date : YYYY-MM-DD 형식으로 받아옴
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        # destination : HND or NRT
        # destination = request.form['destination']
        destination = 0

        # int 형식으로 비용 받아옴.
        budget = int(request.form['budget'])

        input_start_date = int(start_date.split('-')[1]) * 100 + int(start_date.split('-')[2])
        input_end_date = int(end_date.split('-')[1]) * 100 + int(end_date.split('-')[2])

        best = model(input_start_date, input_end_date, budget)

        best = best.reset_index(drop=True)

        best['walk_time'] = best['walk_time'].astype(int)
        best['total_cost'] = best['total_cost'].astype(int)

        if type(best) != pd.DataFrame:
            error_code = 1
            return render_template('result_reco.html', error_code=error_code)
        else:
            return render_template('result_reco.html',
                                   start_date=start_date,
                                   end_date=end_date,
                                   destination=destination,
                                   budget=budget,
                                   best_df=best
                                   )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9900)
