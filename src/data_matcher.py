import pickle
import re
import csv
import pandas as pd


from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder


#조건을 입력하면 경비를 예측해주는 코드
#  날짜, 지역 등 매칭되는 리스트를 불러온 후 해당 리스트를 검토하여 저장, 조합하여 경비 산출. 산출된 경비 제시.
#  ml을 통한 대략적인 예측치 제시
#  단순통계를 통한 대략적인 예측치도 제시

#경비 및 조건을 입력하면 경로를 추천해주는 코드
#  날짜, 지역 등 매칭되는 리스트를 불러온 후 해당 리스트를 검토하여 저장, 조합하여 경비 산출. 조건 이상의 경비는 모두 자름
#  남은 리스트중 상위권에 분포하는 것들을 모아 제시

#  모든 서비스에서, 항공편의 출발/도착시간, 이동시간은 물론 *숙소까지의 이동시간* 과 *숙소까지 이동했을때의 왕복경비*를 제공해주는 것이 포인트


########환경에따라 바꿀 변수
filepath='./idleproject/src/'


def make_daterange(date1, date2):
    date_range=[]
    if date2 < 631 or date1 > 700:
        date_range=[x for x in range(date1, date2)]
    else:
        date_range=[x for x in range(date1, 631)]+[y for y in range(701, date2)]


    return date_range

def date_to_day(date):
    dayofweek={7:'토',1:'일',2:'월',3:'화',4:'수',5:'목',6:'금'}
    #date에서 week, 요일 추출
    m=date//100
    d=date-m*100
    if m==6: 
        mkey=4
    if m==7: 
        mkey=6
    w=(d+mkey-1)//7
    d=mkey+d-7*w
    return dayofweek[d]


def timeadd(a,b):
    min=int(a.split(':')[0])*60+int(a.split(':')[1])
    min=min+b+60 #공항 수속시간 1시간 추가
    h=min//60
    m=min%60
    if h >= 24: 
        h-=24
    h=int(h)
    m=int(m)

    return str(h).zfill(2)+':'+str(m).zfill(2)+':00'

kor_depart=['GMP', 'ICN']
jpn_depart=['HND', 'NRT']
cand_arriv={'GMP':'HND', 'HND':'GMP', 'ICN':'NRT', 'NRT':'ICN'}

#입력된 조건에 맞는 항공권 리스트 추리기
def make_flist(flight_file, cond):
    
    #,index,Date,Day,Airline,Departure time,Departure airport,Arrival time,Arrival airport,Flight time,Price
    cand_date=[x for x in range(cond['Date_from'],cond['Date_to']+1)]
    #cand_time=[x for x in range(cond['Departure time_from'],cond['Departure time_to']+1)]
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

#입력된 조건에 맞는 숙박 리스트 추리기
def make_alist(acc_file, cond):
    
    cand_date=make_daterange(cond['Date_from'],cond['Date_to'])
    for date in cand_date:
        idx=str(date)
        a_result=acc_file[acc_file[idx]!='0']

    return a_result

#리스트들을 받아서 숙박/항공 조합 만들기
def combination(f_list1,f_list2, a_list, cond): #bound=0이면 제약 없이 수집
    #교통 추가정보:
    #'Time_Cost_NRT', 'Money_Cost_NRT', 'Time_Walk_NRT','Time_Cost_HND', 'Money_Cost_HND', 'Time_Walk_HND'
    rec_list=pd.DataFrame()
    cand_date=make_daterange(cond['Date_from'],cond['Date_to'])


    a_list['hotel cost']=0

    for date in cand_date:
        idx=str(date)
        a_list['hotel cost']+=a_list[idx]

    f_list2.rename(columns=lambda x: x+'_return', inplace=True)
    f_list1=f_list1[f_list1['Price'] <= cond['bound']/2]
    f_list2=f_list2[f_list2['Price_return'] <= cond['bound']/2]
    a_list=a_list[0 < a_list['hotel cost']]

    a_list=a_list[a_list['hotel cost'] <= cond['bound']/2]

    print('candidate num:',f_list1.shape[0]*f_list2.shape[0]*a_list.shape[0])

    for fidx1, flight1 in f_list1.iterrows():
        for fidx2, flight2 in f_list2.iterrows():
            for aidx, acc in a_list.iterrows():
                if flight1['Arrival airport']=='HND':
                    total_cost = flight1['Price']+acc['Money_Cost_HND']
                    arrival_time = timeadd(flight1['Arrival time'],acc['Time_Cost_HND'])
                    walk_time=acc['Time_Walk_HND']
                elif flight1['Arrival airport']=='NRT':
                    total_cost = flight1['Price']+acc['Money_Cost_NRT']
                    arrival_time = timeadd(flight1['Arrival time'],acc['Time_Cost_NRT'])
                    walk_time=acc['Time_Walk_NRT']

                if flight2['Departure airport_return']=='HND':
                    total_cost += flight2['Price_return']+acc['Money_Cost_HND']
                elif flight2['Departure airport_return']=='NRT':
                    total_cost += flight2['Price_return']+acc['Money_Cost_NRT']

                total_cost+=acc['hotel cost']


                if total_cost <= cond['bound'] or cond['bound']==0:
                    new=pd.concat([flight1,flight2])
                    new=pd.concat([new,acc[['Hotel Name','Hotel Address','Hotel Score']]])
                    new['hotel cost']=acc['hotel cost']
                    new['arrival_time']=arrival_time
                    new['walk_time']=walk_time
                    new['total_cost']=total_cost
                    rec_list=pd.concat([rec_list,new], axis=1)


    return rec_list.transpose()

#숙박/항공 조합을 만들고 그중 저렴한 탑10개 뽑기
def model(input_date1, input_date2, bound):

    flight_file = pd.read_csv(filepath+'precleaning_flight_df.csv')
    #acc_file=pd.read_csv(filepath+'hotel_plus_metro_final.csv')
    acc_file=pd.read_csv(filepath+'hotel_plus_metro_afterfilledA.csv')
    flight_file['Price']=flight_file['Price'].astype(int)

    #사용자가 입력하는 조건들을 아래 dict의 변수로 주도록 설정.
    cond={
        'Date_from':input_date1, #601형태로 입력값을 변환해야 함
        'Date_to':input_date2,
        'Day':0,##미사용
        'Airline':0,##미사용
        'Departure time_from':0,##미사용
        'Departure time_to':0,##미사용
        'Departure airport':'KOR',
        'Hotel Address':0,
        'Hotel Score':0,##미사용
        'Walk_dist':0,##미사용
        'bound':bound
    }


    cond_plane={
        'Date_from':input_date1, #601형태로 입력값을 변환해야 함
        'Date_to':input_date1,
        'Day':0,##미사용
        'Airline':0,##미사용
        'Departure time_from':0,##미사용
        'Departure time_to':0,##미사용
        'Departure airport':'KOR',
        'Hotel Address':0,
        'Hotel Score':0,##미사용
        'Walk_dist':0,##미사용
        'bound':bound
    }

    cond_plane_return={
        'Date_from':input_date2, #601형태로 입력값을 변환해야 함
        'Date_to':input_date2,
        'Day':0,##미사용
        'Airline':0,##미사용
        'Departure time_from':0,##미사용
        'Departure time_to':0,##미사용
        'Departure airport':'JPN',
        'Hotel Address':0,
        'Hotel Score':0,##미사용
        'Walk_dist':0,##미사용
        'bound':bound
    }


    f_list1=make_flist(flight_file,cond_plane)
    f_list2=make_flist(flight_file,cond_plane_return)

    a_list=make_alist(acc_file, cond)

    rec_list=combination(f_list1, f_list2, a_list, cond)
    print('comb complete')
    try:
        rec_list = rec_list.sort_values(by=['total_cost'], axis=0)
        best = rec_list.head(10)
        return best
    except:
        return 'No Result'
    

#bound 설정시 예산을 줬을 때 그 안에서 최적해를, 안주면 조건에 맞는 최적해 자체를 줌.

################################## ml prediction ######################################

def pred_by_ml_plane(input_date, input_airport):
    
    with open(filepath+"flight_last.pkl", 'rb') as file:
        lr3 = pickle.load(file)

    with open(filepath+"flight_ohe.pkl", 'rb') as file:
        enc3 = pickle.load(file)

    Xres=pd.DataFrame(columns=['Date','Day','Departure airport','Arrival airport'])
    input_data = {'Date':[input_date],'Day':[date_to_day(input_date)],'Departure airport':[cand_arriv[input_airport]],'Arrival airport':[input_airport]}
    tmp=pd.DataFrame(input_data)
    Xres = pd.concat([Xres,tmp], ignore_index=True)

    Xres['Date']=Xres['Date'].astype(int)
    Xres['Date']=(Xres['Date'])//100+((Xres['Date']).mod(100)//7)/10 #월/일이 아니라 월/주로 분리
    Xres=enc3.transform(Xres).toarray()
    result= lr3.predict(Xres) 
    return result[0]

def pred_by_stat_plane(input_date, input_airport):
    
    planes = pd.read_csv(filepath+'precleaning_flight_df.csv')
    planes=planes[planes['Arrival airport']==input_airport]
    planes['Dateforcalc']=planes['Date'].str.split('-').str[1].astype(int)*100+planes['Date'].str.split('-').str[2].astype(int)
    planes=planes[planes['Dateforcalc']==input_date]
    result = round(planes['Price'].mean())

    return result

def pred_by_ml_hotel(input_date, input_airport):
    
    df = pd.read_csv(filepath+'hotel_plus_metro_afterfilledA.csv')
    #df = pd.read_csv(filepath+'hotel_plus_metro_final.csv')
    input_date=str(input_date)

    tdf=df[df[input_date]!=0]
    if input_airport=='NRT':
        transportation_cost=round(df['Money_Cost_NRT'].mean())
    elif input_airport=='HND':
        transportation_cost=round(df['Money_Cost_HND'].mean())
    
    q1=round(tdf[input_date].quantile(.35))
    q2=round(tdf[input_date].quantile(.5))
    q3=round(tdf[input_date].quantile(.65))

    return q1, q2, q3, transportation_cost

def pred_by_ml(input_date1, input_date2, input_airport):
    date_range=[]
    date_range=make_daterange(input_date1, input_date2)
    plain1=pred_by_ml_plane(input_date1, input_airport)
    plain2=pred_by_ml_plane(input_date2, cand_arriv[input_airport])
    res1=0
    res2=0
    res3=0
    trans_total=0
    for date in date_range:
        q1, q2, q3, transportation_cost=pred_by_ml_hotel(date, input_airport)
        res1+=q1
        res2+=q2
        res3+=q3
        trans_total=transportation_cost*2
    total1=res1+trans_total+plain1+plain2
    total2=res2+trans_total+plain1+plain2
    total3=res3+trans_total+plain1+plain2
    return plain1, plain2, res1, res2, res3, trans_total, total1, total2, total3


def compare_ml_stat():
    drange=[x for x in range(601, 631)]+[y for y in range(701, 731)]
    lst=[]
    for airport in ['GMP', 'ICN','HND', 'NRT']:
        for date in drange:
            a=pred_by_ml_plane(date,airport)
            b=pred_by_stat_plane(date, airport)
            print(date, airport, a, b, abs(a-b))
            lst.append( abs(a-b))
    print(max(lst))


if __name__ == "__main__":


    print(pred_by_ml(601, 602, 'HND'))
    print(pred_by_ml(601, 602, 'NRT'))

    best=model(601, 602, 500000)
    print(best)
