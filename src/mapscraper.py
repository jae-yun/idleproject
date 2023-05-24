#selenium에서 사용할 모듈 import
import time
import requests
from bs4 import BeautifulSoup
import re
import csv

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 

yen=9.56

def timedecomp(txt):
    numbers = re.findall(r'\d+', txt)
    numbers = list(map(int, numbers))
    id1=txt.find('시간')
    id2=txt.find('분')
    res=0
    if id1!=-1 and id2!=-1:
        res=numbers[0]*60+numbers[1]
    elif id1==-1 and id2!=-1:
        res=numbers[0]
    elif id1!=-1 and id2==-1:
        res=numbers[0]*60
    return res

def wait_input(driver):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "tactile-searchbox-input"))
        ) #입력창이 뜰 때까지 대기
    finally:
        pass


def pre_list(output_file):
    prelist=[]
    inf = open(output_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf)
    for line in rdr:
        prelist.append(line[0])

    inf.close()
    return prelist
    

def transport_calc(driver, input_file, output_file, error_search, prelist):

    airport=['Narita Airport Transport, 1-1 후루고메 나리타시 Chiba 286-0104 일본', '하네다국제공항']

    inf = open(input_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf)
    outf = open(output_file, 'a', encoding='utf-8')
    wr = csv.writer(outf)
    #대중교통으로 변경
    search_box_from = driver.find_element(By.XPATH, '//*[@id="omnibox-directions"]/div/div[2]/div/div/div/div[3]/button').click()
    '''
    #출발 시간 토글로 변경
    driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/span/div/div/div/div[2]').click()
    driver.find_element(By.XPATH, '//*[@id=":33"]/div').click()

    #비행기 시간에 맞추어 시간 설정
    search_box_time = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div/span[1]/input')
    search_box_time.send_keys('오후 1:00')
    '''
    search_box_from = driver.find_element(By.XPATH, '//*[@id="sb_ifc50"]/input')
    search_box_to = driver.find_element(By.XPATH, '//*[@id="sb_ifc51"]/input')

    for line in rdr:
        accommodation=line[0]
        adr=line[1]
        

        if accommodation not in prelist:
            new=line
        
            search_box_from.send_keys(airport[0])

            search_box_to.clear()
            search_box_to.send_keys(adr) 

            search_box_to.send_keys(Keys.ENTER)
            time.sleep(3.0)

            try:
                time_cost0=driver.find_element(By.XPATH, '//*[@id="section-directions-trip-0"]/div[1]/div/div[1]/div').text
            except:
                #주소 입력이 잘 되지 않으면 아래 코드로
                adr2=adr.split('도쿄')[0]+' 일본'
                search_box_to.clear()
                search_box_to.send_keys(adr2) 

                search_box_to.send_keys(Keys.ENTER)
                time.sleep(3.0)

            try:
                time_cost0=driver.find_element(By.XPATH, '//*[@id="section-directions-trip-0"]/div[1]/div/div[1]/div').text
                time_cost0=timedecomp(time_cost0)
                money_cost0=driver.find_element(By.XPATH, '//*[@id="section-directions-trip-0"]/div[1]/div/div[3]/span[1]').text
                money_cost0=int(re.sub(r'[^0-9]', '', money_cost0))*yen
                money_cost0=round(money_cost0)
                time_walk0=driver.find_element(By.XPATH, '//*[@id="section-directions-trip-0"]/div[1]/div/div[3]/span[2]').text
                time_walk0=timedecomp(time_walk0)

                time.sleep(2.0)

                search_box_from.clear()
                search_box_from.send_keys(airport[1])
                search_box_to.send_keys(Keys.ENTER)

                time.sleep(3.0)

                time_cost1=driver.find_element(By.XPATH, '//*[@id="section-directions-trip-0"]/div[1]/div/div[1]/div').text
                time_cost1=timedecomp(time_cost1)
                money_cost1=driver.find_element(By.XPATH, '//*[@id="section-directions-trip-0"]/div[1]/div/div[3]/span[1]').text
                money_cost1=int(re.sub(r'[^0-9]', '', money_cost1))*yen
                money_cost1=round(money_cost1)
                time_walk1=driver.find_element(By.XPATH, '//*[@id="section-directions-trip-0"]/div[1]/div/div[3]/span[2]').text
                time_walk1=timedecomp(time_walk1)
                time.sleep(2.0)

                new+=[time_cost0, money_cost0, time_walk0, time_cost1, money_cost1, time_walk1]
                wr.writerow(new)

            except:
                error_search.append(accommodation)
                print(accommodation, 'failed')
            
    inf.close()
    outf.close()

def init_list(input_file, output_file):
    inf = open(input_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf)
    for line in rdr:
        indline=line
        break #index line만 가져오기
    indline+=['Time_Cost_NRT', 'Money_Cost_NRT', 'Time_Walk_NRT','Time_Cost_HND', 'Money_Cost_HND', 'Time_Walk_HND']
    outf = open(output_file, 'w', encoding='utf-8')
    wr = csv.writer(outf)
    wr.writerow(indline)
    outf.close()
    inf.close()

if __name__ == "__main__":

    # 옵션 생성
    options = webdriver.ChromeOptions()

    # 옵션 추가
#    options.add_argument("--lang=en-GB")
#    options.add_argument('disable-gpu') # GPU를 사용하지 않도록 설정
    #options.add_argument('headless')

    # 브라우저 옵션을 적용하여 드라이버 생성
    driver = webdriver.Chrome('chromedriver', options=options) 
    #driver = webdriver.Chrome('chromedriver') 


    link = 'https://www.google.com/maps/dir/'

    driver.get(link)

    wait_input(driver) #검색창 나올때까지 기다리기
    
    # driver , link = selenium_setting() # selenium사용을 위한 셋팅

    ############################사용자 환경에 맞춰 수정
    filepath='./idleproject/src/'

    input_file=filepath+'hotel.csv'
    output_file=filepath+'hotel_plus_metro.csv'

    prelist=pre_list(output_file)
    if len(prelist) <=1:
        init_list(input_file, output_file)

    error_search = []
    transport_calc(driver, input_file, output_file, error_search, prelist)
    driver.quit()