import re
import csv
import pandas as pd
#조건을 입력하면 경비를 예측해주는 코드
#  날짜, 지역 등 매칭되는 리스트를 불러온 후 해당 리스트를 검토하여 저장, 조합하여 경비 산출. 산출된 경비 제시.
#  ml을 통한 대략적인 예측치 제시
#  단순통계를 통한 대략적인 예측치도 제시

#경비 및 조건을 입력하면 경로를 추천해주는 코드
#  날짜, 지역 등 매칭되는 리스트를 불러온 후 해당 리스트를 검토하여 저장, 조합하여 경비 산출. 조건 이상의 경비는 모두 자름
#  남은 리스트중 상위권에 분포하는 것들을 모아 제시

#  모든 서비스에서, 항공편의 출발/도착시간, 이동시간은 물론 *숙소까지의 이동시간* 과 *숙소까지 이동했을때의 왕복경비*를 제공해주는 것이 포인트


def timeadd(a,b):
    min=a.str.split(':').str[0].astype(int)*60+a.str.split(':').str[1].astype(int)
    min=min+b+60 #공항 수속시간 1시간 추가
    h=min//60
    m=min%60
    if h > 24: 
        h-=24

    return str(h).zfill(2)+':'+str(m).zfill(2)+':00'

kor_depart=['GMP', 'ICN']
jpn_depart=['HND', 'NRT']
cand_arriv={'GMP':'HND', 'HND':'GMP', 'ICN':'NRT', 'NRT':'ICN'}


def make_flist(flight_file, cond):
    
    #,index,Date,Day,Airline,Departure time,Departure airport,Arrival time,Arrival airport,Flight time,Price
    cand_date=[x for x in range(cond['Date_from'],cond['Date_to']+1)]
    cand_time=[x for x in range(cond['Departure time_from'],cond['Departure time_to']+1)]
    if cond['Departure airport']=='KOR':
        cand_airport=kor_depart
    elif cond['Departure airport']=='JPN':
        cand_airport=jpn_depart    
    else:
        cand_airport=[cond['Departure airport']]

    flight_file['Dateforcalc']=flight_file['Date'].str.split('-').str[1].astype(int)*100+flight_file['Date'].str.split('-').str[2].astype(int)

    f_result=flight_file[flight_file['Dateforcalc'].isin(cand_date)]
    f_result=f_result[f_result['Departure airport'].isin(cand_airport)]

    return f_result

def make_alist(acc_file, cond):


    cand_date=[x for x in range(cond['Date_from'],cond['Date_to']+1)]
    for date in cand_date:
        idx=str(date)
        a_result=acc_file[acc_file[idx]!='0']

    return a_result

def combination(f_list, a_list, cond): #bound=0이면 제약 없이 수집
    #교통 추가정보:
    #'Time_Cost_NRT', 'Money_Cost_NRT', 'Time_Walk_NRT','Time_Cost_HND', 'Money_Cost_HND', 'Time_Walk_HND'
    rec_list=pd.DataFrame
    cand_date=[x for x in range(cond['Date_from'],cond['Date_to']+1)]

    for fidx, flight in f_list.iterrows():
        for aidx, acc in a_list.iterrows():
            if flight['Arrival airport']=='HND':
                total_cost = flight['Price']+acc['Money_Cost_HND']
                for date in cand_date:
                    idx=str(date)
                    total_cost+=acc[idx]
                arrival_time = timeadd(flight['Arrival time'],acc['Time_Cost_HND'])

            if total_cost <= cond['bound'] or cond['bound']==0:
                new=pd.concat([flight,acc])
                new['arrival_time']=arrival_time
                new['total_cost']=total_cost
                rec_list=pd.concat([rec_list,new], axis=1)
    return rec_list.transpose()

def model(flight_file, acc_file, cond):
    f_list=make_flist(flight_file,cond)
    a_list=make_alist(acc_file, cond)

    rec_list=combination(f_list, a_list, cond)
    rec_list.sort_values(by=['Price'], axis=0)
    best = rec_list.loc[0:9]
    return best

#bound 설정시 예산을 줬을 때 그 안에서 최적해를, 안주면 조건에 맞는 최적해 자체를 줌.


def predbyml(cond):

    return

def predbystat():
    return




if __name__ == "__main__":
    flight_file = pd.read_csv('precleaning_flight_df.csv')
    acc_file=pd.read_csv('hotel.csv')
    flight_file['Price']=flight_file['Price'].astype(int)
    #accfile 가격 전처리

    cond={
        'Date_from':601, #601형태로 입력값을 변환해야 함
        'Date_to':602,
        'Day':0,##미사용
        'Airline':0,##미사용
        'Departure time_from':0,##미사용
        'Departure time_to':0,##미사용
        'Departure airport':'KOR',
        'Hotel Address':0,
        'Hotel Score':0,##미사용
        'Walk_dist':0,##미사용
        'bound':0
    }

    best=[]
    best=model(flight_file, acc_file, cond)




