import time
import os
import csv
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

prelist=[]

def to_coord(date):
    #date에서 week, 요일 추출
    m=date//100
    d=date-m*100
    if m==6: 
        mkey=4
        m=1
    if m==7: 
        mkey=6
        m=2  
    w=(d+mkey-1)//7
    d=mkey+d-2*w
    w+=1
    return m, w, d

def crawl_hotel(driver, input_file, prelist):
    #part1: 새 호텔 업데이트 및 가격정보 크롤링
    newprice={}
    #현재 csv파일의 column 길이 추출 - 신규 데이터용 pad 만들기
    inf = open(input_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf, quotechar = "'", quoting = csv.QUOTE_ALL)
    for line in rdr:
        length = len(line)-3
        break #index line만 가져오기
    inf.close()
    pad=[0 for x in range(length)]

    file =  open(input_file, 'a', encoding='utf-8')
    writer = csv.writer(file)

    while True:#div class :  "dd023375f5"
        hotel_links = driver.find_elements(By.CLASS_NAME, "e13098a59f") # 호텔 링크들 수집(리스팅 된 호텔의 공동 class_name)

        for i in range(len(hotel_links)):
            hotel_links = driver.find_elements(By.CLASS_NAME, "e13098a59f") # 호텔 링크들을 다시 수집 (새로고침 때문에 stale element가 될 수 있으므로)
            main_window = driver.current_window_handle # 기존 탭 저장
            hotel_url = hotel_links[i].get_attribute("href") # 호텔 링크 url가져오기
            #print(hotel_url)
                
            driver.execute_script("window.open('');") # 새 탭 열기
            driver.switch_to.window(driver.window_handles[1]) # 새 탭으로 전환
            driver.get(hotel_url) # 새 탭에서 url 로드
            time.sleep(5)
            # ActionChains(driver).key_down(Keys.CONTROL).click(hotel_links[i]).key_up(Keys.CONTROL).perform()  # 호텔 클릭 시 새 탭으로 열기
            # time.sleep(10)

            if len(driver.window_handles) > 1: # 탭이 1개 보다 많을 때 탭 전환 (기존 리스팅 되어있는 탭 외에 새 탭으로 개별 호텔 페이지가 열려야함)
            #     driver.switch_to.window(driver.window_handles[1])

                try:
                    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "d2fee87262")))
                    time.sleep(5)
                    
                    hotel_name = driver.find_element(By.CLASS_NAME, "d2fee87262").text
                    if hotel_name not in prelist:
                        hotel_address = driver.find_element(By.CSS_SELECTOR, '.hp_address_subtitle.js-hp_address_subtitle.jq_tooltip').text
                        
                        #hotel_star_elements = str(driver.find_elements(By.XPATH, '//*[@id="hp_hotel_name"]/span'))
                        #hotel_star = hotel_star_elements.count("b6dc9a9e69")
                        '''                        
                        try:
                            hotel_star_elements = str(driver.find_elements(By.XPATH, '//*[@id="hp_hotel_name"]/span/span[1]/div/span/div/span'))
                        except:
                            hotel_star_elements = str(driver.find_elements(By.XPATH, '//*[@id="hp_hotel_name"]/span/span[2]/div/span/div/span'))
                        finally:
                            hotel_star = hotel_star_elements.count("b6dc9a9e69")
                        '''
                        hotel_score = driver.find_element(By.CSS_SELECTOR, '#js--hp-gallery-scorecard > a > div > div > div > div.b5cd09854e.d10a6220b4').text
                        writer.writerow([hotel_name, hotel_address, hotel_score]+pad) #pad로 다른 데이터들과 길이 맞추기
                        prelist.append(hotel_name)
                        
                    hotel_price = driver.find_element(By.CLASS_NAME, 'bui-price-display__value').text
                    newprice[hotel_name]=hotel_price



                except Exception as e: #예외처리 
                    print(f"Error in getting info from hotel page: {e}")

                driver.close()
                driver.switch_to.window(main_window) # 탭 전환
            else:
                print(f"Error: New tab did not open for hotel {i}")

            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dd023375f5")))

        # try: # 다음 페이지로 이동 (기존코드)
        #     next_page_button = driver.find_element(By.XPATH, '//*[@id="search_results_table"]/div[2]/div/div/div[4]/div[2]/nav/div/div[3]/button') # 페이지 넘기기
        #     if next_page_button:
        #         next_page_button.click()
        #         time.sleep(5)
        #     else:
        #         break
        # except NoSuchElementException:
        #     file.close()
        #     return newprice
        
        #아래는 마지막페이지에서 무한루프 막기 위한 수정코드 
        try: 
            next_page_button = driver.find_element(By.XPATH, '//*[@id="search_results_table"]/div[2]/div/div/div[4]/div[2]/nav/div/div[3]/button')
            if next_page_button.get_attribute("disabled"):  # 다음 페이지 버튼의 disabled 속성 확인
                break
            else:
                next_page_button.click()
                time.sleep(5)
        except NoSuchElementException:
            break

    file.close()
    return newprice


def update_price(input_file, output_file, date, newprice):
    #part2: 가격 업데이트
    inf = open(input_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf, quotechar = "'", quoting = csv.QUOTE_ALL)
    outf = open(output_file, 'w', encoding='utf-8')
    wr = csv.writer(outf)
    #index 작성
    newprice["Hotel Name"]=date

    for line in rdr:
        acc_name=line[0]
        if acc_name in newprice.keys():
            new=line+[newprice[acc_name]]
            wr.writerow(new)
        else:
            new=line+[0]
            wr.writerow(new)
   
    inf.close()
    outf.close()

        


def wait_input(driver):
    try:
        element=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id=":Ra9:"]')))
    finally:
        pass

#이미 정보를 수집한 호텔들을 모아두는 리스트
def pre_list(output_file):
    prelist=[]
    inf = open(output_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf, quotechar = "'", quoting = csv.QUOTE_ALL)
    for line in rdr:
        if line:  # 리스트가 비어 있지 않은지 확인(index error 발생해서 추가(임나래))
            prelist.append(line[0])

    inf.close()
    return prelist
    
def init_list(input_file):
    outf = open(input_file, 'w', encoding='utf-8')
    wr = csv.writer(outf)
    wr.writerow(["Hotel Name", "Hotel Address", "Hotel Score"]) #이터레이션이 돌면 날짜가 추가됨
    outf.close()

def get_date(input_file):
    inf = open(input_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf, quotechar = "'", quoting = csv.QUOTE_ALL)
    for line in rdr:
        indline=line
        break #index line만 가져오기 
    date = indline[-1]
    inf.close()
    if date=="Hotel Score": #날짜 데이터가 없다면 601을 출력
        date=600
    else:
        date=int(date)

    if date==630:
        date=701
    else:
        date+=1
    return date
       
def overwrite(input_file, output_file):
    #다음 이터레이션을 위해 결과파일을 입력파일에 덮어씌움
    inf = open(input_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf, quotechar = "'", quoting = csv.QUOTE_ALL)
    outf = open(output_file, 'w', encoding='utf-8')
    wr = csv.writer(outf)
    for line in rdr:
        wr.writerow(line)     
    inf.close()
    outf.close()


if __name__ == "__main__":

    chrome_options = webdriver.ChromeOptions()

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    url = 'https://www.booking.com/'
    driver.get(url)
    wait_input(driver)

    #아래 경로는 환경마다 수정
    #input_file='./src/hotel.csv'
    #output_file='./src/hotel_tmp.csv'
    input_file='C:/Users/lovel/Desktop/project4/teampj/hotel2.csv'  
    output_file='C:/Users/lovel/Desktop/project4/teampj/hotel_tmp.csv'   


    #이미 정보를 수집한 호텔들을 모아두는 리스트
    prelist=pre_list(input_file)
    if len(prelist) <=1:
        init_list(input_file)

    #검색 시작 날짜 설정
    init_date=get_date(input_file) 
    #검색 날짜 범위 설정
    if init_date < 631:
        date_range=[x for x in range(init_date, 631)]+[y for y in range(701, 731)]
    else:
        date_range=[x for x in range(init_date, 731)]
    

    time.sleep(2)
    try:
        driver.find_element(By.XPATH, '//*[@id="b2indexPage"]/div[22]/div/div/div/div[1]/div[1]/div/button').click() #팝업창 닫기 버튼 누르기(여기서 페이지 넘어갈 때 시간 좀 걸림! 기다리면 됨)
    except:
        time.sleep(1)
    time.sleep(2)

    driver.find_element(By.XPATH, '//*[@id="indexsearch"]/div[2]/div/div/form/div[1]/div[1]/div/div').click() # 도시 검색창 클릭 
    time.sleep(1)

    driver.find_element(By.XPATH, '//*[@id=":Ra9:"]').send_keys("신주쿠")  #검색창에 신주쿠 입력 
    time.sleep(1)

    driver.find_element(By.XPATH, '//*[@id="indexsearch"]/div[2]/div/div/form/div[1]/div[2]/div/div[1]/button[1]').click() # 날짜 선택창 클릭
    time.sleep(1)

    driver.find_element(By.XPATH, '//*[@id="calendar-searchboxdatepicker"]/div/div[1]/button').click()  # 달력 페이지 넘기기 
    time.sleep(1)

    first_run = True

    for date in date_range:
        wait = WebDriverWait(driver, 15)
        
        if first_run:
            # 체크인날짜 변경
            m, w, d = to_coord(date)
            checkin_xpath = f'//*[@id="calendar-searchboxdatepicker"]/div/div[1]/div/div[{m}]/table/tbody/tr[{w}]/td[{d}]'
            change_checkin = wait.until(EC.element_to_be_clickable((By.XPATH, checkin_xpath))).click()

            if date == 630:
                next_date = 701
            else:
                next_date = date + 1

            # 체크아웃날짜 변경
            m, w, d = to_coord(next_date)
            checkout_xpath = f'//*[@id="calendar-searchboxdatepicker"]/div/div[1]/div/div[{m}]/table/tbody/tr[{w}]/td[{d}]'
            change_checkout = wait.until(EC.element_to_be_clickable((By.XPATH, checkout_xpath))).click()

            # 검색버튼 클릭
            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id=":Ra9:"]')))
            search_button.send_keys(Keys.ENTER)
            time.sleep(10)

            # 호텔 체크박스
            # checkbox_xpath = '//*[@id="filter_group_ht_id_:R24q:"]/div[10]/label/span[2]' # 빌라 체크박스 경로(리스팅 적은 걸로 테스트용)
            checkbox_xpath = '//*[@id="filter_group_ht_id_:R24q:"]/div[4]/label/span[2]' # 호텔 체크박스 경로
            hotel_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, checkbox_xpath)))
            hotel_checkbox.click()
            time.sleep(10)

            # 테스트용 옵션! (15-20 예산 선택(케이스2개라서!))
            # highprice_checkbox_xpath = '//*[@id="filter_group_pri_:Rcq:"]/div[2]/div[3]/label/span[2]'
            # highprice_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, highprice_checkbox_xpath)))
            # highprice_checkbox.click()
            # time.sleep(10)

            first_run = False
        else:
            change_date_xpath = '//*[@id="b2searchresultsPage"]/div[3]/div/div/div/form/div[1]/div[2]/div/div[1]' # 날짜 변경
            change_date = wait.until(EC.element_to_be_clickable((By.XPATH, change_date_xpath))).click()
            
            # 체크인날짜 변경
            m, w, d = to_coord(date)
            checkin_xpath = f'//*[@id="calendar-searchboxdatepicker"]/div/div[1]/div/div[1]/table/tbody/tr[{w}]/td[{d}]'
            change_checkin = wait.until(EC.element_to_be_clickable((By.XPATH, checkin_xpath))).click()

            if date == 630:
                next_date = 701
            else:
                next_date = date + 1

            # 체크아웃날짜 변경
            m, w, d = to_coord(next_date)
            checkout_xpath = f'//*[@id="calendar-searchboxdatepicker"]/div/div[1]/div/div[1]/table/tbody/tr[{w}]/td[{d}]'
            change_checkout = wait.until(EC.element_to_be_clickable((By.XPATH, checkout_xpath))).click()

            # 검색버튼 클릭
            search_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id=":Ra9:"]')))
            search_button.send_keys(Keys.ENTER)
            time.sleep(10)

            
            # 호텔 체크박스 #지우기
            # hotel_checkbox_xpath = '//*[@id="filter_group_ht_id_:R24q:"]/div[10]/label/span[2]' # 빌라 체크박스 경로(리스팅 적은 걸로 테스트용)
            # hotel_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, hotel_checkbox_xpath)))
            # hotel_checkbox.click()
            # time.sleep(10)

            # 테스트용 옵션! (15-20 예산 선택(케이스2개라서!))
            # highprice_checkbox_xpath = '//*[@id="filter_group_pri_:Rcq:"]/div[2]/div[3]/label/span[2]'
            # highprice_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, highprice_checkbox_xpath)))
            # highprice_checkbox.click()
            # time.sleep(10)

            # 호텔 체크박스 : 필터에서 호텔 선택
            hotel_checkbox_xpath = '//*[@id="filter_group_ht_id_:R2cq:"]/div[4]/label/span[2]' 
            hotel_checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, hotel_checkbox_xpath)))
            hotel_checkbox.click()
            time.sleep(5)

        # 여기서 크롤링코드
        newprice = crawl_hotel(driver, input_file, prelist)
        update_price(input_file, output_file, date, newprice)
        overwrite(output_file, input_file) # 기록된 결과를 다음 이터레이션을 위해 인풋 파일에 기록

        
    driver.quit()



#코드 돌아가는 플로우:
#크롤링이 오래걸리는 만큼 끊었다가 다시 하는 경우를 상정.
#prelist로 이미 수집된 호텔들을 체크
#get date로 며칠까지 크롤링이 완료되었던 것인지, 혹은 지금이 크롤링 시작인지 체크하여 다음 시작 날짜 설정

#접속 후 크롤링(이부분에서 무한루프중...)
#크롤링 도중에, prelist에 없는 호텔을 발견하면 점수까지 수집하여 호텔 리스트에 추가(날짜가 바뀌어도 점수가 바뀌지는 않으므로 다른 정보는 재수집할 필요 없음)
#리스트 기재 여부와 상관없이 가격정보를 모두 딕셔너리 형태로 저장

#update_price코드로 다음단계 진행. 임시파일을 열고, 
#기존 파일의 각 행을 불러와 가격정보가 있다면 가격정보 추가, 없다면 0을 추가하여 임시파일에 기록
#overwrite 코드를 통해 임시파일을 기존파일에 덮어씌움. 이것으로 기존 파일은 새로운 호텔/새로운 가격정보를 가지고 업데이트됨

#날짜를 바꾸어 크롤링/update price/overwrite반복