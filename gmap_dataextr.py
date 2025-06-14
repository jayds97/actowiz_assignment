#!/usr/bin/env python
# coding: utf-8

# In[12]:


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
import re
import pandas as pd
from os.path import exists
import os
import csv


# In[13]:


# Setup Chrome options
options = Options()
# options.add_argument("--headless=new")  # Headless mode (invisible browser)
options.add_argument("--window-size=1920,1080")
options.set_capability("goog:loggingPrefs", {"performance": "ALL"})


# In[14]:


CLEANR = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
def cleanhtml(raw_html):
    cleantext =re.sub(CLEANR, '', str(raw_html))
    return cleantext


# In[15]:


out_csv = 'Near_location.csv'
input_folder = "Near_location"

csv_exists = exists(out_csv)
if csv_exists:
    print(f"csv exists in path {out_csv},removing now ....")
    os.remove(out_csv)
    
df = pd.DataFrame(columns=['Name','Address1','Address2','Time_Distane'])
header_list=df.columns
print(f"creating new CSV...")
df.to_csv(out_csv,sep="|",index=False,header=False)


# In[16]:


parent_dir = "/home/data/input"
path = os.path.join(parent_dir, input_folder) 
file_exists = exists(path)
if not file_exists :
        os.makedirs(path)
else:
    print("Path Already Exits")


# In[17]:

#Name of the outlet eg mcdonald's,starbucks,GAS Station,Dominos
business_name = input("Enter the name outlet (For Example mcdonald's,starbucks,GAS Station)\n")
#Name of the Location eg JFK Arrport
location = input("Enter location name\n")
final_string = business_name +' near '+ location
new_slug = final_string
print(final_string)


# In[18]:


def distance_time(durl):
    #print ("Calculating Time and Distance",durl)
    new_durl = "distance_time"+str(durl)
    new_durl = re.sub(r'[<>:"/\\|?*!&=]', '_', str(new_durl))
    new_durl = re.sub(r'\s+', '_', new_durl)
    new_durl = re.sub(r'%', '_', new_durl)
    new_durl = new_durl[:200]  # trim if too long
    file_exists = exists('/home/data/input/'+str(input_folder)+'/'+str(new_durl)+'.html')
    if file_exists:
        pass
    else:
        driver.get(durl)
        time.sleep(5)
        direction = driver.find_element(By.CSS_SELECTOR, ".Cw1rxd.google-symbols.NhBTye.G47vBd")
        
        direction.click()
        time.sleep(5)
        desinput = driver.find_element("xpath", '//*[@id="sb_ifc50"]/input')
        desinput.clear()  # Optional: clear any existing value
        desinput.send_keys(location + Keys.ENTER)
        time.sleep(5)
        with open('/home/data/input/'+str(input_folder)+'/'+str(new_durl)+'.html', "w", encoding='utf-8') as f:
                f.write(driver.page_source)

    HTMLFile = open('/home/data/input/'+str(input_folder)+'/'+str(new_durl)+'.html', "r")
    dtpage = HTMLFile.read()
    #lpage = re.sub('\\n',' ',str(lpage))
    dtpage = re.sub('amp;','',str(dtpage))
    drmodes = re.findall('directions-trip-travel-mode(.*?)</div><div><h1',str(dtpage))
    
    
    
    return drmodes


# In[19]:


def parse_loc(lpage,final_string,full_url):
    #print('hiiiiii')
    try:
        name = re.findall('<span class="a5H0ec"></span>\s*(.*?)\s*<',str(lpage))[0]
    except:
        name =""
    try:
        add = re.findall('aria-label="Address:\s*(.*?)\s*"',str(lpage))[0]
    except:
        add = ""
        
    try:
        add2 = re.findall('pane\.wfvdle25" aria-label="\s*(.*?)\s*"',str(lpage))[0]
        
    except:
        add2 =""
    
        
    time_n_distance = distance_time(full_url)
    #print(type(time_n_distance))
    final_time_distancex =""
    for cut in time_n_distance:
        mode_of_transport = re.findall('class="Os0QJc google-symbols.*?aria-label="\s*(.*?)\s*"',str(cut))[0]
        time = re.findall('div class="Fk3sm.*?>\s*(.*?)\s*<',str(cut))[0]
        distance = re.findall('div class="ivN21e tUEI8e.*?>\s*(.*?)\s*</div>',str(cut))[0]
        distance = cleanhtml(distance)
        temp_dist = distance
        final_dist =0 
        if 'mile' in temp_dist:
            temp_dist = re.sub('miles', '', str(temp_dist), flags=re.IGNORECASE)
            temp_dist = re.sub('mile', '', str(temp_dist), flags=re.IGNORECASE)
            temp_dist = re.sub('mi', '', str(temp_dist), flags=re.IGNORECASE)
            temp_dist = re.sub(r'\s+', '', str(temp_dist))
            final_dist = float(temp_dist) * 1.60934
            final_dist = round(float(final_dist), 2)
            
            if final_dist > 25:
                mode_of_transport =""
                time = ""
            final_dist = str(final_dist) + 'KM'
        
        else:
            final_dist = distance
            
        if mode_of_transport and time :
            final_time_distancex =str(final_time_distancex)+' '+'Mode of Transport: ' +str(mode_of_transport)+' '+'Distance: '+final_dist+' '+"Time:" + str(time)
            
            
            
    
            
            
            
            
            
            
            
            
            
            
            
    if final_time_distancex:   
        
        my_dict={}
        my_dict['Name'] = name
        my_dict['Address1'] = add
        my_dict['Address2'] = add2
        my_dict['Time_Distane'] = final_time_distancex




        list1=list(my_dict.values())
        #print(f"writing to csv .... ")
        with open(out_csv, 'a', newline='') as file:
            #deli='|'
            writer = csv.DictWriter(file,fieldnames=header_list)
            # Write the header row if the file is empty
            if file.tell() == 0:
                writer.writeheader()
            # Write the data row
            writer.writerow(my_dict)    
    print(name)
    print(final_time_distancex)
        
    


# In[20]:


def fetch_details(ppage,final_string):

    listing = re.findall(' href="https://www.google.com/maps/place(.*?)"',str(ppage))
    for lurl in listing:

        full_url = "https://www.google.com/maps/place" + str(lurl)
        new_listing = full_url
        new_listing = re.sub(r'[<>:"/\\|?*!&=]', '_', str(new_listing))
        new_listing = re.sub(r'\s+', '_', new_listing)
        new_listing = re.sub(r'%', '_', new_listing)
        new_listing = re.sub(r'\.', '_', new_listing)
        new_listing = new_listing[:200]  # trim if too long
        #new_listing = new_listing.replace('/','_').replace(':','_').replace('.','').replace('\s+','')
        file_exists = exists('/home/data/input/'+str(input_folder)+'/'+str(new_listing)+'.html')
        if file_exists:
            pass
        else:
            driver.get(full_url)
            time.sleep(5)
            with open('/home/data/input/'+str(input_folder)+'/'+str(new_listing)+'.html', "w", encoding='utf-8') as f:
                    f.write(driver.page_source)

        HTMLFile = open('/home/data/input/'+str(input_folder)+'/'+str(new_listing)+'.html', "r")
        lpage = HTMLFile.read()
        #lpage = re.sub('\\n',' ',str(lpage))
        lpage = re.sub('amp;','',str(lpage))
        parse_loc(lpage,final_string,full_url)

    
                
            


# In[21]:


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
new_url = new_slug.lower()
print(new_url)
new_url = new_url.replace('/','_').replace(':','_').replace('.','').replace(' ','')
file_exists = exists('/home/data/input/'+str(input_folder)+'/'+str(new_url)+'.html')
if file_exists:
    pass
    
    
else:
   
    driver.get("https://www.google.com/maps/")
    Finput = driver.find_element("xpath", '//*[@id="searchboxinput"]')
    Finput.clear()  # Optional: clear any existing value
    Finput.send_keys(final_string + Keys.ENTER)
    time.sleep(5)
    element = driver.find_element(By.CSS_SELECTOR, ".fontTitleLarge.IFMGgb")
    element.click()
    num_down_presses = 100
    for i in range(num_down_presses):
        time.sleep(1)
        try:

            driver.find_element(By.CLASS_NAME, "HlvSq")
            print("Element with class 'HlvSq' found. Stopping scroll.")
            break
        except:
            # Not found yet – keep scrolling
            actions = ActionChains(driver)
            actions.send_keys(Keys.ARROW_DOWN)
            actions.perform()
    #     actions = ActionChains(driver)
    #     actions.send_keys(Keys.ARROW_DOWN)
    #     actions.perform()
    # Save page source to HTML file
    with open('/home/data/input/'+str(input_folder)+'/'+str(new_url)+'.html', "w", encoding='utf-8') as f:
                f.write(driver.page_source)
            
            
HTMLFile = open('/home/data/input/'+str(input_folder)+'/'+str(new_url)+'.html', "r")
ppage = HTMLFile.read()
#ppage = re.sub('\\n',' ',str(ppage))
ppage = re.sub('amp;','',str(ppage))
fetch_details(ppage,final_string)
    





    


# In[22]:


driver.quit()


# In[ ]:




