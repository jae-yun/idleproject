import re
import csv

#조건을 입력하면 경비를 예측해주는 코드
#  날짜, 지역 등 매칭되는 리스트를 불러온 후 해당 리스트를 검토하여 저장, 조합하여 경비 산출. 산출된 경비 제시.
#  ml을 통한 대략적인 예측치 제시
#  단순통계를 통한 대략적인 예측치도 제시

#경비 및 조건을 입력하면 경로를 추천해주는 코드
#  날짜, 지역 등 매칭되는 리스트를 불러온 후 해당 리스트를 검토하여 저장, 조합하여 경비 산출. 조건 이상의 경비는 모두 자름
#  남은 리스트중 상위권에 분포하는 것들을 모아 제시

#  모든 서비스에서, 항공편의 출발/도착시간, 이동시간은 물론 *숙소까지의 이동시간* 과 *숙소까지 이동했을때의 왕복경비*를 제공해주는 것이 포인트




def make_list(flight_file, acc_file, cond):
    f_result=[]
    inf = open(flight_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf, quotechar = "'", quoting = csv.QUOTE_ALL)
    
    for line in rdr:
        if cond==1:
            f_result.append(line)
    inf.close()

    a_result=[]
    inf = open(acc_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf, quotechar = "'", quoting = csv.QUOTE_ALL)
    
    for line in rdr:
        if cond==1:
            a_result.append(line)
    inf.close()

    return f_result, a_result

def combination(f_list, a_list, bound=0):
    rec_list=[]
    for flight in f_list:
        for acc in a_list:
            total_cost = flight[0]+acc[0]
            if total_cost <= bound or bound==0:
                arrival_time = flight[0]+acc[0]
                new=flight+acc+[arrival_time, total_cost]
                rec_list.append(new)
    return rec_list

def model(flight_file, acc_file, cond, bound):
    f_list=[]
    a_list=[]
    f_list, a_list=make_list(flight_file, acc_file, cond)
    rec_list=[]
    rec_list=combination(f_list, a_list, bound)
    rec_list.sort() #additional cond.
    best = rec_list[0:9]    
    return best

#bound 설정시 예산을 줬을 때 그 안에서 최적해를, 안주면 조건에 맞는 최적해 자체를 줌.


def predbyml(cond):

    return

def predbystat():
    return




if __name__ == "__main__":
    best=[]
    best=model(flight_file, acc_file, cond, bound)
