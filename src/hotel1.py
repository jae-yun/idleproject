import os
import csv
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def crawl_hotel(driver):
    with open('hotel_df2.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Date", "Hotel Name", "Hotel Address", "Hotel Price", "Hotel Star", "Hotel Score"])

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
                        date = driver.find_element(By.XPATH, '//*[@id="hp_availability_style_changes"]/div[2]/div/div/form/div[1]/div[1]/div/div/button[1]').text # 날짜만 
                        #date = driver.find_element(By.XPATH, '//*[@id="basiclayout"]/div[2]/div[1]/div/div[1]/div[2]/div/form/div/div[3]/div[2]/button').text
                        #print(date)
                        hotel_name = driver.find_element(By.CLASS_NAME, "d2fee87262").text
                        hotel_address = driver.find_element(By.CSS_SELECTOR, '.hp_address_subtitle.js-hp_address_subtitle.jq_tooltip').text
                        hotel_price = driver.find_element(By.CLASS_NAME, 'bui-price-display__value').text
                        hotel_star_elements = driver.find_elements(By.XPATH, '//span[@data-testid="rating-stars"]/span')
                        '''
                        raw_score = str(rr.select_one('span'))
                        parsed_score = 5-raw_score.count("star-display__half")/2-raw_score.count("star-display__empty")

                        
                        '''
                        hotel_star = len(hotel_star_elements)
                        hotel_score = driver.find_element(By.CSS_SELECTOR, '#js--hp-gallery-scorecard > a > div > div > div > div.b5cd09854e.d10a6220b4').text

                        writer.writerow([date, hotel_name, hotel_address, hotel_price, hotel_star, hotel_score])

                    except Exception as e: #예외처리 
                        print(f"Error in getting info from hotel page: {e}")

                    driver.close()
                    driver.switch_to.window(main_window) # 탭 전환
                else:
                    print(f"Error: New tab did not open for hotel {i}")

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "dd023375f5")))

            try: # 다음 페이지로 이동
                next_page_button = driver.find_element(By.XPATH, '//*[@id="search_results_table"]/div[2]/div/div/div[4]/div[2]/nav/div/div[3]/button') # 페이지 넘기기
                if next_page_button:
                    next_page_button.click()
                    time.sleep(5)
                else:
                    break
            except NoSuchElementException:
                break


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
    rdr = csv.reader(inf, quotechar = "'", quoting = csv.QUOTE_ALL)
    for line in rdr:
        prelist.append(line[0])

    inf.close()
    return prelist
    
def init_list(output_file):
    outf = open(output_file, 'w', encoding='utf-8')
    wr = csv.writer(outf)
    wr.writerow(["Hotel Name", "Hotel Address", "Hotel Star", "Hotel Score"]) #날짜 추가 필요
    outf.close()

def init_iter(input_file, output_file, date):
    inf = open(input_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf, quotechar = "'", quoting = csv.QUOTE_ALL)
    for line in rdr:
        indline=line
        break #index line만 가져오기
    indline.append(date) #새 날짜 추가
    outf = open(output_file, 'w', encoding='utf-8')
    wr = csv.writer(outf)
    wr.writerow(indline)
    outf.close()
    inf.close()

def get_date(input_file):
    inf = open(input_file, 'r', encoding='utf-8')
    rdr = csv.reader(inf, quotechar = "'", quoting = csv.QUOTE_ALL)
    for line in rdr:
        indline=line
        break #index line만 가져오기 
    date = indline[-1]
    inf.close()
    return date
       

if __name__ == "__main__":

    chrome_options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    url = 'https://www.booking.com/'
    driver.get(url)
    time.sleep(5)

    driver.find_element(By.XPATH, '//*[@id="b2indexPage"]/div[22]/div/div/div/div[1]/div[1]/div/button').click() #팝업창 닫기 버튼 누르기(여기서 페이지 넘어갈 때 시간 좀 걸림! 기다리면 됨)
    time.sleep(10)

    driver.find_element(By.XPATH, '//*[@id="indexsearch"]/div[2]/div/div/form/div[1]/div[1]/div/div').click() # 도시 검색창 클릭 
    time.sleep(1)

    driver.find_element(By.XPATH, '//*[@id=":Ra9:"]').send_keys("신주쿠")  #검색창에 신주쿠 입력 
    time.sleep(1)

    driver.find_element(By.XPATH, '//*[@id="indexsearch"]/div[2]/div/div/form/div[1]/div[2]/div/div[1]/button[1]').click() # 날짜 선택창 클릭
    time.sleep(1)

    driver.find_element(By.XPATH, '//*[@id="calendar-searchboxdatepicker"]/div/div[1]/button').click()  # 달력 페이지 넘기기 
    time.sleep(1)

    # 6월 한달 검색을 위해 for문 사용하여 달력 일자 클릭
    week_num = 5
    day_num = 7

    first_run = True # 첫 번째 실행을 위한 플래그 설정

    for week in range(1, week_num + 1):
        for day in range(1, day_num + 1):
            if not first_run : 
                wait = WebDriverWait(driver, 15)
                #  체크인날짜 변경
                checkin_xpath = f'//*[@id="calendar-searchboxdatepicker"]/div/div[1]/div/div[1]/table/tbody/tr[{week}]/td[{day}]'
                change_checkin = wait.until(EC.element_to_be_clickable((By.XPATH, checkin_xpath))).click()
                    
                # 체크아웃날짜 변경
                checkout_xpath = f'//*[@id="calendar-searchboxdatepicker"]/div/div[1]/div/div[1]/table/tbody/tr[{week+1}]/td[{day+1}]'
                change_checkout = wait.until(EC.element_to_be_clickable((By.XPATH, checkout_xpath))).click()
                    
                # 검색버튼 클릭 
                driver.find_element(By.XPATH, '//*[@id="b2searchresultsPage"]/div[3]/div/div/div/form/div[1]/div[4]/button').click() 
                time.sleep(10)   
            
                # 호텔 체크박스 
                driver.find_element(By.XPATH, '//*[@id="filter_group_ht_id_:R2cq:"]/div[4]/label/span[2]').click() 
                time.sleep(10)

                # 여기서 크롤링코드 
                crawl_hotel(driver)
                time.sleep(10)

            try:
                if first_run :
                    # 체크인 날짜 클릭 => 달력 xpath guide : /div[Month]/table/tbody/tr[Week]/td[Day] 
                    xpath_in = f'//*[@id="calendar-searchboxdatepicker"]/div/div[1]/div/div[1]/table/tbody/tr[1]/td[5]' 
                    driver.find_element(By.XPATH, xpath_in).click() 
                    time.sleep(1)

                    # 체크아웃 날짜 클릭
                    xpath_out = f'//*[@id="calendar-searchboxdatepicker"]/div/div[1]/div/div[1]/table/tbody/tr[1]/td[6]'
                    driver.find_element(By.XPATH, xpath_out).click() 
                    time.sleep(1)

                    # '검색' 버튼 클릭  
                    driver.find_element(By.XPATH, '//*[@id="indexsearch"]/div[2]/div/div/form/div[1]/div[4]/button').click() 
                    time.sleep(1)  

                    # 호텔 체크박스 
                    driver.find_element(By.XPATH, '//*[@id="filter_group_ht_id_:R24q:"]/div[4]/label/span[2]').click() 
                    time.sleep(5)

                    # 여기서 크롤링코드 
                    crawl_hotel(driver)
                    time.sleep(10)
                
                first_run = False

            except:
                pass
            
    input()