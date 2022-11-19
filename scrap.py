#!/usr/bin/env python
# coding: utf-8

# In[130]:


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

options = Options()
ua = UserAgent()
userAgent = ua.random
options.add_argument(f'user-agent={userAgent}')

#access to the path of your chromedriver.exe
driver = Chrome('C:/Users/HP/Downloads/inec_scum/chromedriver.exe')
#the homepage since you have to sign in first before navigating to the required page for sign in
driver.get("https://cvr.inecnigeria.org/Home/start")
#waits until your page loads completely before sign in process begins
driver.implicitly_wait(20)

#sign in cuse using xpath and the id of the html properties as key as well ass value for login button
driver.find_element_by_xpath("""//*[@id="LoginEmail"]""").send_keys('georgemichaeldagogo@gmail.com')
driver.find_element_by_xpath("""//*[@id="LoginPassword"]""").send_keys('ayabagreen1')
driver.find_element_by_xpath("""//*[@value="Log in"]""").click()

#navigates to the page for inputting state, LGA,AREA id and polling unit
driver.get("https://cvr.inecnigeria.org/VotersRegister")
driver.implicitly_wait(6)

select1 = Select(driver.find_element_by_id('VoterRegisterStateId'))
#selecting by value instead of state name
select1.select_by_value('1')
select2 = Select(driver.find_element_by_id('VoterRegisterLocalGovernmentId'))
select2.select_by_value('1')
select3 = Select(driver.find_element_by_id('VoterRegisterRegistrationAreaId'))
#at a point the values sudden increase exponentially like from 22 to 61373
select3.select_by_value('1')
select4 = Select(driver.find_element_by_id('VoterRegisterPollingUnitId'))
select4.select_by_value('1')

#waits for page is ready then switches to the reCAPTCHA iframe
WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,"//iframe[@title='reCAPTCHA']")))
#clicks on the reCAPTCHA button and it either verifies without image test or it doesn't. currently at 8 out of 10 times with 8 being verification without image test
WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.recaptcha-checkbox-border"))).click()


time.sleep(5)
#switches from reCAPTCHA iframe back to default reCAPTCHA else your code will gives error about not recognizing the next xpath
driver.switch_to.default_content()
#clicks on display button
driver.find_element_by_xpath("""//*[@value="DISPLAY REGISTER"]""").click()
driver.implicitly_wait(20)
names = []
loca = []
contents =driver.find_elements_by_class_name("table.table-condensed.table-borderless.condensed-rows.voter")
for i in contents:
    name = i.get_attribute('innerText')
    names.append(name)
location =driver.find_elements_by_class_name("table.table-bordered.table-striped.afterpagebreak.bg-white")
for s in location:
    local= s.get_attribute('innerText')
    loca.append(local)
    


driver.quit()


# In[144]:


import pandas as pd

af = pd.DataFrame(loca,columns =['area'])
#af = af.replace('\n', ',')
af.area = af.area.apply(lambda x: x.replace('\n', ','))
af.area = af.area.apply(lambda x: x.replace('\t', ','))
af.area = af.area.apply(lambda x: x.replace('LGA:,', ''))
af.area = af.area.apply(lambda x: x.replace(',POLLING UNIT:', ''))
af.area = af.area.apply(lambda x: x.replace(',WARD:', ''))
af.area = af.area.apply(lambda x: x.replace(',DELIM:', ''))
af.area = af.area.apply(lambda x: x.replace(',RECORDS:', ''))

af = af['area'].str.split(",", n = 5, expand = True)
af.columns = ['LGA', 'Polling_unit', 'Ward', 'Delim','Records']
af


# In[145]:


#my_string="hello python world , i'm a beginner"
#print(my_string.split("world",1)[1])
import pandas as pd

df = pd.DataFrame(names,columns =['Names'])
df = df.replace('\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0\xa0', '')
df.Names = df.Names.apply(lambda x: x.replace('\t\n\t', ','))
df.Names = df.Names.apply(lambda x: x.replace('\n\n', ','))
df.Names = df.Names.apply(lambda x: x.replace('VIN:', ''))
df.Names = df.Names.apply(lambda x: x.replace('DOB-Y:', ''))
df.Names = df.Names.apply(lambda x: x.replace('GENDER:', ','))
df = df['Names'].str.split(",", n = 7, expand = True)
df.columns = ['no_', 'First_name', 'Last_name', 'VIN','DOB','Gender']
df


# In[152]:


import pandas as pd
uf = pd.concat([df, af], axis=1)
uf= uf.fillna(method='ffill')
uf


# In[ ]:




