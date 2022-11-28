#!/usr/bin/env python
# coding: utf-8

# ## Automated Data Extraction
# ### Webscraps INEC Database

def inec_webscrap(state_opt,lga_opt,ward_opt,polling_opt):
    #driver for Chrome
    from selenium.webdriver import Chrome
    #selector for dropdown
    from selenium.webdriver.support.ui import Select
    #waits until a process or page is accessible 
    from selenium.webdriver.support.ui import WebDriverWait
    #By.XPATH, By.CSS_SELECTOR etc
    from selenium.webdriver.common.by import By
    #manipulates properties of chrome driver like add fake user agent
    from selenium.webdriver.chrome.options import Options
    #certain conditions need to be met before a process begins
    from selenium.webdriver.support import expected_conditions as EC
    #this changes the useragent name which reduces reCAPTCHA verification
    from fake_useragent import UserAgent
    #allows code to sleep for a little time until process is completely done
    import time
    #to get nothing more than 5 random pages
    import random
    #this allows the random list to be sorted
    import more_itertools as mit
    #pandas cause why not
    import pandas as pd
    #needed for saving .csv
    import os
    #needed for picture download through link
    import requests

    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')

    #access to the path of your chromedriver.exe
    driver = Chrome('the path to where your own chromedriver.exe is located in your system.')
    #the homepage since you have to sign in first before navigating to the required page for sign in
    driver.get("https://cvr.inecnigeria.org/Home/start")
    #waits until your page loads completely before sign in process begins
    driver.implicitly_wait(20)

    #sign in cuse using xpath and the id of the html properties as key as well ass value for login button
    driver.find_element_by_xpath("""//*[@id="LoginEmail"]""").send_keys('your email')
    driver.find_element_by_xpath("""//*[@id="LoginPassword"]""").send_keys('your password')
    driver.find_element_by_xpath("""//*[@value="Log in"]""").click()

    #navigates to the page for inputting state, LGA,AREA id and polling unit
    driver.get("https://cvr.inecnigeria.org/VotersRegister")
    driver.implicitly_wait(6)

    select1 = Select(driver.find_element_by_id('VoterRegisterStateId'))
    #selecting by value instead of state name
    select1.select_by_visible_text(state_opt)
    select2 = Select(driver.find_element_by_id('VoterRegisterLocalGovernmentId'))
    select2.select_by_visible_text(lga_opt)
    select3 = Select(driver.find_element_by_id('VoterRegisterRegistrationAreaId'))
    select3.select_by_visible_text(ward_opt)
    select4 = Select(driver.find_element_by_id('VoterRegisterPollingUnitId'))
    select4.select_by_visible_text(polling_opt)

    #waits for page is ready then switches to the reCAPTCHA iframe
    #WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@title='reCAPTCHA']")))
    #clicks on the reCAPTCHA button and it either verifies without image test or it doesn't. currently at 8 out of 10 times with 8 being verification without image test
    #WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.recaptcha-checkbox-border"))).click()

    time.sleep(10)
    #switches from reCAPTCHA iframe back to default reCAPTCHA else your code will gives error about not recognizing the next xpath
    driver.switch_to.default_content()
    #clicks on display button
    driver.find_element_by_xpath("""//*[@value="DISPLAY REGISTER"]""").click()
    driver.implicitly_wait(20)
    names = []
    loca = []
    pictures = []
    pages = []
    #required data can be found in the table with class name below that contains the name, gender, date of birth and vin for everyone in that page
    contents =driver.find_elements_by_class_name("table.table-condensed.table-borderless.condensed-rows.voter")
    for i in contents:
        name = i.get_attribute('innerText')
        names.append(name)
    #required data can be found in the table with class name below that contains the lga, polling unit, area and delim for everyone
    location =driver.find_elements_by_class_name("table.table-bordered.table-striped.afterpagebreak.bg-white")
    for s in location:
        local= s.get_attribute('innerText')
        loca.append(local)
    #to get the pictures of the registered voters under the img tag
    picture = driver.find_elements_by_css_selector("img")
    for p in picture:
        pic= p.get_attribute('src')
        pictures.append(pic)
    #this is to get the extent of the pages like "page 1 of 50"
    page = driver.find_elements_by_class_name("col-lg-12.text-right.nav-text")
    for a in page:
        pag= a.text
        pages.append(pag)

    def all_pages(web_page):
        """this function takes the next webpage https://cvr.inecnigeria.org/voters_register/index/display/page:2 as a
            parameter and returns the basic information of the registered voters in a polling unit as well as their pictures 
             and appends it to the universal list with the appopriate name
        """
        driver.get(web_page)
        contents =driver.find_elements_by_class_name("table.table-condensed.table-borderless.condensed-rows.voter")
        for i in contents:
            name = i.get_attribute('innerText')
            names.append(name)
        picture = driver.find_elements_by_css_selector("img")
        for p in picture:
            pic= p.get_attribute('src')
            pictures.append(pic)

    #after raw extract of the pages the content was split
    q =[item.split() for item in pages]
    #the extent of the page number has the below index
    page_no = q[0][5] 
    #it must be an integar or else it can't be parsed into the variable list a that has a range 
    page_num = int(page_no)
    #this list is a formatted string that returns only 5 random inec display pages based on the page_num and returns the main page if the page_num is 1,
    a = [f'https://cvr.inecnigeria.org/voters_register/index/display/page:{i:d}' for i in (mit.random_combination(range(2, page_num), r=5))] if page_num >= 7 else [f'https://cvr.inecnigeria.org/voters_register/index/display/page:{i:d}' for i in (mit.random_combination(range(2, page_num), r=page_num -2))] if 3 <= page_num <= 6 else ['https://cvr.inecnigeria.org/voters_register/index/display/page:2'] if page_num == 2 else ['https://cvr.inecnigeria.org/voters_register/index']
    #a = [f'https://cvr.inecnigeria.org/voters_register/index/display/page:{i:d}' for i in range(2, page_num +1 , 1)] 

    #this loop uses the a variable list and runs a loop for every page increment using 
    # the all_pages function that returns the basic info and pictures and appends it to the required list awaiting 
    #  awaiting cleaning and wrangling
    for o in a:
        all_pages(o)
    #ends the driver process

    driver.quit()

    #turns the area list into a pandas dataframe and changes '\n' and '\t' to ','
    #also changes the other repeated headers to nothing
    af = pd.DataFrame(loca,columns =['area'])
    af.area = af.area.apply(lambda x: x.replace('\n', '|'))
    af.area = af.area.apply(lambda x: x.replace('\t', '|'))
    af.area = af.area.apply(lambda x: x.replace('LGA:|', ''))
    af.area = af.area.apply(lambda x: x.replace('|POLLING UNIT:', ''))
    af.area = af.area.apply(lambda x: x.replace('|WARD:', ''))
    af.area = af.area.apply(lambda x: x.replace('|DELIM:', ''))
    af.area = af.area.apply(lambda x: x.replace('|RECORDS:', ''))
    af = af['area'].str.split("|",n = 6, expand = True)
    af.columns = ['LGA', 'Polling_unit', 'Ward', 'Delim','Records']
    #af = af.drop(['new1','new2'], axis=1)

    df = pd.DataFrame(names,columns =['Names'])
    df = df.replace('\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0', '')
    df.Names = df.Names.apply(lambda x: x.replace('\t\n\t', '|'))
    df.Names = df.Names.apply(lambda x: x.replace('\n\n', '|'))
    df.Names = df.Names.apply(lambda x: x.replace('VIN:', ''))
    df.Names = df.Names.apply(lambda x: x.replace('DOB-Y:', ''))
    df.Names = df.Names.apply(lambda x: x.replace('GENDER:', '|'))
    df = df['Names'].str.split("|",n=6, expand = True)
    df.columns = ['no_', 'Voters_name', 'VIN','DOB','Gender']
    df = df.drop(['no_'], axis=1)

    #concats both df and af datafrmaes together
    ed = pd.concat([df, af], axis=1)
    #since the af dataframe only has one row that corresponds to the df counterpart, fill the nan values with anything above it
    ed= ed.fillna(method='ffill')
   
    unwanted = {'https://cvr.inecnigeria.org/assets/img/myvoter.png','https://cvr.inecnigeria.org/img/logo.png'}

    pictures = [ele for ele in pictures if ele not in unwanted]

    ed['Picture_link'] = pictures

    if (os.path.exists('.\\'+state_opt+'\\'+state_opt+".csv") == False):
        ed.to_csv('.\\'+state_opt+'\\'+state_opt+'.csv',index=False)
    else:
        ed.to_csv('.\\'+state_opt+'\\'+state_opt+'.csv', mode='a', index=False, header=False)
        
    first_message = "Five random pages for {polling} polling unit in the {areaing} ward of {lgaing} LGA has been successfully webscraped \n{numbe} rows were cleaned and saved in {stateing} .csv".format(polling = polling_opt,areaing =ward_opt,lgaing = lga_opt,numbe = len(ed),stateing=state_opt)
    print(first_message)
    second_message = "{} pictures of voters are currently been downloaded to your current path, \nplease have data and avoid using GLO or MTN on edge browser".format(len(ed))
    print(second_message)
    print('Downloading Pictures, please be patient, this is a python code not RUST or Java')

    def download_pic(pict,name):
        url = pict
        filename = '.\\'+state_opt+'\\'+str(name)+'.jpg'
        r = requests.get(url, allow_redirects=True)
        open(filename, 'wb').write(r.content)

    for pi,na in zip(ed.Picture_link,ed.VIN):
        download_pic(pi,na)
        
        
    print('All pictures assigned to their respective VINs have successfully been downloaded, please keep up the good work') 
    return ed


# ### State List Extraction



from selenium.webdriver import Chrome
#selector for dropdown
from selenium.webdriver.support.ui import Select
#waits until a process or page is accessible 
from selenium.webdriver.support.ui import WebDriverWait
#By.XPATH, By.CSS_SELECTOR etc
from selenium.webdriver.common.by import By
#manipulates properties of chrome driver like add fake user agent
from selenium.webdriver.chrome.options import Options
#certain conditions need to be met before a process begins
from selenium.webdriver.support import expected_conditions as EC
#this changes the useragent name which reduces reCAPTCHA verification
from fake_useragent import UserAgent
#allows code to sleep for a little time until process is completely done
import time
#to get nothing more than 5 random pages
import random
#this allows the random list to be sorted
import more_itertools as mit
#pandas cause why not
import pandas as pd
#needed for saving .csv
import os
#needed for picture download through link
import requests
import json


#function to save the state_list nested list as a .json file after extraction.
def save_state(state_name, state_list):
    filename = state_name+'.json'
    with open(filename, 'w') as f:
        json.dump(state_list, f)


#function to load the state_list saved as .json file into your Jupyter environment
def read_state(filename):
    f = open(filename)
    state_list = json.load(f)
    f.close()
    return (state_list)



def statelist_func(list_of_state):
    options = Options()
    ua = UserAgent()
    userAgent = ua.random
    options.add_argument(f'user-agent={userAgent}')

    #access to the path of your chromedriver.exe
    driver = Chrome(r'the path to where chromedriver is located in your local machine.')
    #the homepage since you have to sign in first before navigating to the required page for sign in
    driver.get("https://cvr.inecnigeria.org/Home/start")
    #waits until your page loads completely before sign in process begins
    driver.implicitly_wait(20)

    #sign in cuse using xpath and the id of the html properties as key as well ass value for login button
    driver.find_element_by_xpath("""//*[@id="LoginEmail"]""").send_keys('youremail@gmail.com')
    driver.find_element_by_xpath("""//*[@id="LoginPassword"]""").send_keys('your password')
    driver.find_element_by_xpath("""//*[@value="Log in"]""").click()

    #navigates to the page for inputting state, LGA,AREA id and polling unit
    driver.get("https://cvr.inecnigeria.org/VotersRegister")
    driver.implicitly_wait(6)

    select1 = Select(driver.find_element_by_id('VoterRegisterStateId'))
    select2 = Select(driver.find_element_by_id('VoterRegisterLocalGovernmentId'))
    select3 = Select(driver.find_element_by_id('VoterRegisterRegistrationAreaId'))

    st =driver.find_elements_by_id("VoterRegisterStateId") 

    for state in list_of_state:
        state_list = [state]
        state_to_extractfrom = state
        select1.select_by_visible_text(state_to_extractfrom)
        time.sleep(1)
        lg =driver.find_elements_by_id("VoterRegisterLocalGovernmentId")
        for lga in lg:
            lga1= lga.get_attribute('innerText')
            lga2 = lga1.replace('\n','|')
            lga3 = lga2.replace('-SELECT-|','')
            extracted_LGA_list = lga3.split('|')
            LGA_list = [[LGA] for LGA in extracted_LGA_list]
            state_list.append(LGA_list)
        for LGA in LGA_list:
            lga_to_extractfrom = LGA[0]
            select1.select_by_visible_text(state_to_extractfrom)
            select2.select_by_visible_text(lga_to_extractfrom)
            time.sleep(1.5)
            wd =driver.find_elements_by_id("VoterRegisterRegistrationAreaId")
            for wda in wd:
                wda1= wda.get_attribute('innerText')
                wda2 = wda1.replace('\n','|')
                wda3 = wda2.replace('--SELECT--|','')
                extracted_ward_list = wda3.split('|')
                ward_list = [[ward] for ward in extracted_ward_list]
                LGA.append(ward_list)
            for ward in ward_list:
                ward_to_extractfrom = ward[0]
                select1.select_by_visible_text(state_to_extractfrom)
                select2.select_by_visible_text(lga_to_extractfrom)
                select3.select_by_visible_text(ward_to_extractfrom)
                time.sleep(2.5)
                po =driver.find_elements_by_id("VoterRegisterPollingUnitId")
                for pol in po:
                    pol1= pol.get_attribute('innerText')
                    pol2 = pol1.replace('\n','|')
                    pol3 = pol2.replace('--SELECT--|','')
                    extracted_pollingunit_list = pol3.split('|')
                    pollingunit_list = [punit for punit in extracted_pollingunit_list]
                    ward.append(pollingunit_list)

        save_state(state_list[0], state_list)
    #print(state_list)      
    driver.quit()




# ### Voter's Records Extraction


#looping through the list to get the arguments for the extraction function for a certain specified state.

#looping through the list to get the arguments for the extraction function for a certain specified state.

def extraction_func(state_list):
    state = state_list[0]
    LGAlist = state_list[1] #assigns the list of LGAs of that particular state to a variable for further looping
    for l_list in LGAlist:
        LGAlist
        LGA = l_list[0] #assigns the current LGA name to a variable to be used by our selenium function
        Wards = l_list[1] #assigns the list of wards of that particular LGA to a variable for further looping
        for w_list in Wards:
            ward = w_list[0] #assigns the current ward name to a variable to be used by our selenium function
            pollingunits = w_list[1] #assigns the list of polls of that particular ward to a variable for further looping
            for polls in pollingunits:
                inec_webscrap(state_opt=state, lga_opt=LGA, ward_opt=ward, polling_opt=polls)


# ### State List Clean Up function in case code is broken by captcha

#in the event that the extraction process is broken

def state_listcleaner(captchabrokenafter, state_list):
    #only use when the code has been broken by the captcha
    LGAlist = state_list[1] #assigns the list of LGAs of that particular state to a variable for further looping
    for l_list in LGAlist:
        Wards = l_list[1] #assigns the list of wards of that particular LGA to a variable for further looping
        counter_1 = LGAlist.index(l_list)
        for w_list in Wards:
            pollingunits = w_list[1] #assigns the list of polls of that particular ward to a variable for further looping
            counter_2 = Wards.index(w_list)
            for polls in pollingunits:
                if polls == captchabrokenafter: 
                #checks for the index of the polling unit last extracted, and remove all before it as they must have been extracted.
                    index = pollingunits.index(polls)
                    del pollingunits[:index+1]
                    del Wards[:counter_2]
                    del LGAlist[:counter_1]
                    break
    return (state_list)






