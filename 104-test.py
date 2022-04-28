import pandas as pd
import re, time, requests
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from bs4 import BeautifulSoup

# 職務關鍵字
jobkey = '工程師'
company = '聯發科'
username =''
password =''
JobArr = []
ignore = ['行銷','數位','類比','製程','設備','維護','工具','電路','硬體','驗證','品質','市場','專利','採購','外包','實習','廠務','生產','元件','測試','機構','對流','研發替代役','維修','驗証','CAD','MIS','佈局','實驗','網路','配件','產品工程師'
,'約聘','應屆','畢業','客戶','射頻','RF','量產','layout','IT','封裝','FAE']

# 加入使用者資訊(如使用什麼瀏覽器、作業系統...等資訊)模擬真實瀏覽網頁的情況
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}

# 查詢的關鍵字
my_params = {'ro':'1', # 限定全職的工作，如果不限定則輸入0
             'keyword': str(company), # 想要查詢的關鍵字
             'area':'6001001000' ',' '6001006000', # 限定在台北&新竹的工作
             'isnew':'30', # 只要最近一個月有更新的過的職缺
             'mode':'l'} # 清單的瀏覽模式

url = requests.get('https://www.104.com.tw/jobs/search/?' , my_params, headers = headers).url

#Dylan 
#windows
driver = webdriver.Chrome()
#Linux
#driver = webdriver.Chrome(executable_path='./chromedriver')
driver.get(url)

### 登入 ###
driver.find_elements_by_xpath('//*[@id="global_bk"]/ul/li[2]/ul/li[6]/a')[0].click()
user = driver.find_element_by_id('username') # Username
user.send_keys(username)
pwd = driver.find_element_by_id('password') # PWD
pwd.send_keys(password)
driver.find_elements_by_xpath('//*[@id="submitBtn"]')[0].click() #Login

### 回到關鍵字網頁 ###

# 網頁的設計方式是滑動到下方時，會自動加載新資料，在這裡透過程式送出Java語法幫我們執行「滑到下方」的動作
for i in range(20): 
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    time.sleep(0.6)
    
# 自動加載只會加載15次，超過之後必須要點選「手動載入」的按鈕才會繼續載入新資料（可能是防止爬蟲）
k = 1
while k != 0:
    try:
        # 手動載入新資料之後會出現新的more page，舊的就無法再使用，所以要使用最後一個物件
        driver.find_elements_by_class_name("js-more-page",)[-1].click() 
        # 如果真的找不到，也可以直接找中文!
        # driver.find_element_by_xpath("//*[contains(text(),'手動載入')]").click()
        print('Click 手動載入，' + '載入第' + str(15 + k) + '頁')
        k = k+1
        time.sleep(1) # 時間設定太短的話，來不及載入新資料就會跳錯誤
    except:
        k = 0
        print('No more Job')

# 透過BeautifulSoup解析資料
soup = BeautifulSoup(driver.page_source, 'html.parser')
List = soup.findAll('a',{'class':'js-job-link'})
print('共有 ' + str(len(List)) + ' 筆資料')

def bind(cate):
    k = []
    for i in cate:
        if len(i.text) > 0:
            k.append(i.text)
    return str(k)

i = 0

while i < len(List):
    
    j = 0
    done=0
    print('正在處理第' + str(i) + '筆，共 ' + str(len(List)) + ' 筆資料')
    content = List[i]

    # 這裡用Try的原因是，有時候爬太快會遭到系統阻擋導致失敗。因此透過這個方式，當我們遇到錯誤時，會重新再爬一次資料！
    try:
        resp = requests.get('https://' + content.attrs['href'].strip('//'))
        soup2 = BeautifulSoup(resp.text,'html.parser')
        
        Jobname = content.attrs['title']
        Joblink = 'https://' + content.attrs['href'].strip('//')
        Companyname = soup2.find_all(['a', 'title'])
        print(f'工作職稱: {Jobname} ')
        print(f'連結路徑: {Joblink} ')
        print(f'公司名稱: {Companyname}')
        
        if jobkey in Jobname and company in str(Companyname):
            for j in ignore:
                if j in Jobname:
                    print(f'這個職缺我不要了, {Jobname}')
                    done=1
                    break
            
            #JobArr.append(Joblink)

            if done==0:
                print(f'沒有排除字, 準備投履歷, {Jobname} ')
                #Move to job page
                driver.get(Joblink)
                
                #Click the button "我要應徵"
                #https://blog.csdn.net/cyjs1988/article/details/75006167
                try:
                    print("Running apply resume")
                    #The contents will be modified, that's why chossing XPATH instead class
                    #BTW, div[16] or div[17] depends on you ever applied or not.
                    try:
                        driver.find_elements_by_xpath('//*[@id="app"]/div[3]/div[16]/div/div/a')[0].click()	
                    except Exception as e:
                        print("div[17]")
                        try:
                            driver.find_elements_by_xpath('//*[@id="app"]/div[3]/div[17]/div/div/a')[0].click()
                        except Exception as e:
                            print("div[15]")  
                            try:
                                driver.find_elements_by_xpath('//*[@id="app"]/div[3]/div[15]/div/div/a')[0].click()
                            except Exception as e:
                                print("NONONON")  
                    
                    """
                    try:
                        driver.find_elements_by_xpath('//*[@id="app"]/div/div[1]/div[2]/div/div/div[2]/div[1]/div/form/div')[0].click()	
                    except Exception as e:
                        print(Exception)  
                    time.sleep(1)
                    """
                    #Switch to resume page. Ready to send resume
                    driver.switch_to.window(driver.window_handles[1])  
                    currenturl = driver.current_url
                    driver.get(currenturl)
                    #print(currenturl)

                    #Select the right cover
                    ele_select = driver.find_element_by_id('applyCover')
                    options = Select(ele_select)
                    options.select_by_value("4068368")
                    time.sleep(3)
                   #driver.implicitly_wait(3)

                    #Send the resume
                    driver.find_elements_by_xpath('//*[@id="apply-resume"]/div/button')[0].click()
                    
                    #Close current windoer and back to start page
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])  
                    
                except Exception as e:
                    print(Exception)                                       

            

        i += 1
        print("Success and Crawl Next 目前正在爬第" + str(i) + "個職缺資訊")
        time.sleep(0.5) # 執行完休息0.5秒，避免造成對方主機負擔
    except Exception as e:
        print(Exception)
        break

### 我也很想先抓職缺 再分別寄送履歷, 但看起來裡面有些欄位會改變, 即便我把URL記錄下來也無法看到flag 變成什麼
'''
while j < len(JobArr):


    try:
        print(JobArr[j])
        driver.get(JobArr[j])
        
        driver.find_elements_by_class_name('apply-button__button')[0].click()
        #WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'apply-button__button'))).click()
        print("running...")

        

        #Switch to resume page. Ready to send resume
        driver.switch_to.window(driver.window_handles[j+1])  
        currenturl = driver.current_url
        driver.get(currenturl)
        #print(currenturl)

        ele_select = driver.find_element_by_id('applyCover')
        options = Select(ele_select)
        options.select_by_value("4068368")

        time.sleep(3)
        driver.find_elements_by_id('btSend').click()
        j += 1
        time.sleep(3)
        
    except Exception as e:
        print(Exception)
        break
'''
    
        
driver.quit()
