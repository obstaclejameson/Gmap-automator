from audioop import add
import pandas as pd
from time import sleep
import selenium
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import re
from webdriver_manager.chrome import ChromeDriverManager
# import requests
import json
import os

chrome_options = webdriver.ChromeOptions()
# chrome = ChromeDriverManager().install()
chrome_options.binary_location=os.environ.get("GOOGLE_CHROME_BIN")
chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome(executable_path=os.environ.get('CHROMEDRIVER_PATH'),options=chrome_options)
# driver = webdriver.Chrome(options=chrome_options,executable_path=chrome)
wait = WebDriverWait(driver, 60)
wait2 = WebDriverWait(driver, 30)

url = ' https://www.google.com/search?q='

SAVE_FOLDER = 'G-Map to WordPress Automator Extracts'
if not os.path.exists(SAVE_FOLDER):
    os.mkdir(SAVE_FOLDER)

with open('keywords.txt','r') as fl:
    keywords = fl.readlines()
    # print(keywords)
# post data
def postdata(data,kywd):
    # prepare html
    with open('updates.txt','w') as fl:
              fl.write('Uploading to wordpress') 
            
    introtemp = readFile()[0]
    endtemp = readFile()[1]
    replc ="keyword"
    replc2 ="Keyword"
    kywd=kywd.replace("\n","").strip()
    if introtemp != "":
        introtemp = introtemp.replace("{"+replc+"}",kywd).replace("{"+replc2+"}",kywd) 
    if endtemp != "":
        endtemp = endtemp.replace("{"+replc+"}",kywd).replace("{"+replc2+"}",kywd) 
    content = introtemp+'<table class="table table-bordered" style="width:100%"><tr> <th style="width:15%">Name</th><th style="width:25%">Address</th><th style="width:5%">Zip Code</th><th style="width:10%">Phone Number</th><th style="width:15%">Website</th></tr>'
    end = endtemp

    for post in data:
        content +="<tr><td>"+post['Title']+"</td><td>"+post['Address']+"</td><td>"+post['ZipCode']+"</td><td>"+post['Phone_Number']+"</td><td>"+post['Website']+"</td></tr>"
    content +='</table><h2>'+kywd+'</h2>'
    count = 1
    for post in data:
        content += "&nbsp;"
        content += "<h3> "+str(count)+". "+post['Title']+"</h3><p><strong>Address: </strong>"+post['Address']+"</p><p><strong>Phone Number: </strong>"+post['Phone_Number']+"</p><p><strong>Website: </strong><a href="+post['Website']+">"+post['Website']+"</a></p>"
        count +=1
    content +=end

    # end
    url = readFile()[3]
    driver.get(url)
    try:
        username = driver.find_element_by_id("user_login")
        password = driver.find_element_by_id("user_pass")
        btn = driver.find_element_by_id("wp-submit")
        username.clear()
        username.send_keys(readFile()[4])
        password.clear()
        password.send_keys(readFile()[5])
        btn.click()
    except:pass    
    sleep(3)
    JS_ADD_TEXT_TO_INPUT = """
    var elm = arguments[0], txt = arguments[1];
    elm.value += txt;
    elm.dispatchEvent(new Event('change'));
    """
    driver.get(url+"/post-new.php")
    post_title = driver.find_element_by_id("title")
    post_title.send_keys(kywd)
    txt_button = driver.find_element_by_id("content-html")
    txt_button.click()
    sleep(2)
    post_content = driver.find_element_by_id("content")
    driver.execute_script(JS_ADD_TEXT_TO_INPUT, post_content, content)
    # post_content.send_keys(content)
    # sleep(5)
    driver.execute_script('window.scrollTo(0, 0);')
    wait2.until(EC.element_to_be_clickable((By.XPATH, '//input[@id="publish"]')))
    btnpost = driver.find_element_by_id("publish")
    btnpost.click()
    sleep(5)
def readFile():
    data = []
    with open('variables.txt','r') as search:
        tags = search.read().split('|')
        
        for tag in tags:
            term = tag.strip().replace('\n\n','\n')
            data.append(term)    
        return data
# keywords = ['dentists in vashi']
introtemp = readFile()[0]
endtemp= readFile()[1]
limit =readFile()[2]
paging = True
def getdata(locations,alldata, kw):
        for lctn in locations:
            website = ''
            try:
                atags = lctn.find_elements_by_xpath('.//a')
                for atag in atags:
                    if atag.get_attribute('href')!='#' and atag.get_attribute('href')!= None and  'https://www.google.com/' not in atag.get_attribute('href'):
                         website = atag.get_attribute('href')
            except:pass
            lctn.click()
            sleep(4)
            wait.until(EC.presence_of_element_located((By.XPATH, '//div[contains(@class,"knowledge-panel")]')))
            box = driver.find_element_by_xpath('//div[contains(@class,"knowledge-panel")]')
            name=""
            try:
                name  = box.find_element_by_xpath('.//h2[@data-attrid="title"]').text
            except:pass
            address=""
            try:
                address  = box.find_element_by_xpath('.//div[@data-attrid="kc:/location/location:address"]').text
                zipcode=''
                zip = re.findall(r'\d+',address)
                if len(zip)>0:
                 zipcode = zip[-1]
            except:pass
            try:
                phn  = box.find_element_by_xpath('.//a[@data-dtype="d3ph"]').text
            except: phn=''
            try:
                arra = address.split(":")
                newa = ''
                for txt in arra[1:]:
                    newa +=' '+txt
                newa = newa.strip()
            except:newa="" 
            data = {
                'Title':name,
                'Address':newa,
                'ZipCode':zipcode,
                'Phone_Number':phn,
                'Website':website

            }
            if name != "" or address != "":
                alldata.append(data)
          
            
            if len(alldata)>int(limit):
                global paging
                paging = False
                break
            print(str(len(alldata))," from" ,kw, " collected")
            with open('updates.txt','w') as fl:
                strng = str(len(alldata))+" from " +kw+ " collected"
                fl.write(strng)
    # print(len(locations))

for keywd in keywords:
    alldata = []
    link = url+keywd+'&tbm=lcl#rlfi' 
    driver.get(link)
    paging=True
    while paging:
        sidebar = '//div[@id="search"]'
        wait.until_not(EC.presence_of_element_located((By.XPATH, '//div[@class="rlfl__loading-overlay baAxxe rlfl__visible"]')))
        wait.until(EC.presence_of_element_located((By.XPATH, sidebar)))
        sidebar = driver.find_element_by_xpath(sidebar)
        locations = sidebar.find_elements_by_xpath('.//div[@jsname="GZq3Ke"]') 
        getdata(locations,alldata,keywd)
        
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, '//a[@id="pnnext"]')))  
            driver.find_element_by_xpath('//a[@id="pnnext"]').click()
            sleep(4)
        except:
            print('done')  
            paging = False
    datajsn = json.dumps(alldata)
    # endpoint = 'https://naushadk20.sg-host.com/api/api?key='+keywd+'&endtmp='+endtemp+'&intro='+introtemp
    # r= requests.post(endpoint,data=datajsn) 
    # print(r.text)     
    postdata(alldata,keywd)  
    df = pd.DataFrame(alldata)
    keywd = keywd.strip()
    df.to_csv(SAVE_FOLDER + '/' +keywd+'.csv',header=True,index=False)



    

