#Importing all the required libraries
import time
import bs4
from bs4 import BeautifulSoup
from selenium.common.exceptions import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import json
import requests
import re

#Function to get name and URL of each specific program from list of live programs in "https://knowthychoice.in/blog/" page
def get_list_of_programs(driver,proglist):

    url = r"https://knowthychoice.in/blog/" #given URL
    
    # Open url and get the knowthychoice html page
    time.sleep(2)
    driver.get(url)
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    #each div tag with class name "blog-post-content" contains information(url,name) of specific program available in the blog
    x = soup.find_all("div", class_="blog-post-content")
    for prog in x:
        a_tag = prog.find('a') #finding a tag which generally is used to insert links into your HTML page
        name=a_tag.get_text()
        url=a_tag.get('href') #href attribute in <a> tag has the url for for each program
        
        ##proglist is list of lists where each sublist contains name of the program and its URL.
        proglist.append([name,url])

    #As there are 3 pages available in the website, we go through all those pages and find any new programs if present
    for i in range(3):
        try:
            #using XPATH and click() to go into next pages
            element= driver.find_element(By.XPATH, '//*[@id="content"]/section[2]/div/div/div[7]/div/nav/ul/li['+str(2+i)+']/a')          
            driver.execute_script('arguments[0].scrollIntoView();', element)
            driver.execute_script('window.scrollBy(0, -200);')
            element.click()
            time.sleep(4)
            html = driver.page_source
            soup = BeautifulSoup(html, features="html.parser")
            x = soup.find_all("div", class_="row ind")
            for clg in x:
                info=clg.find("div",class_="td-wrap")
                a_tag = clg.find('a')
                name=a_tag.get_text()
                url=a_tag.get('href')
                #Checking if the program is already explored or not
                if [name,url] in  proglist:
                    continue
                else:
                    proglist.append([name,url])
        except:
            pass

    return proglist

#Function to get concepts covered in each page of specific program available in "https://knowthychoice.in/blog/" page
def get_concepts_covered(driver,proglist):
    all_programs_info = {} #a dictionary(collection of key, value pairs) where keys are names of programs and  values are list of concepts covered 

    for prog in proglist:
        program_name = prog[0]
        url = prog[1]

        time.sleep(2)
        #Open url and get the specific program html page
        driver.get(url)
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        #each div tag of class "col-lg-10 mx-auto" has all the ul tags where each ul tag contains information of different sections available
        x = soup.find("div", class_="col-lg-10 mx-auto")
        all_ul_tags = x.find_all('ul') #finding all <ul> tags

        #In each page last ul tag has the concepts covered, so we use that <ul> tag
        #from ul tag we find all <li> tags and extract info from them.
        concepts = [li_tag.get_text() for li_tag in all_ul_tags[-1].find_all('li')]

        #finally updating the dictionary
        all_programs_info.update({program_name:concepts})

    #all the results are dumped into output.json file
    with open("output.json", "w") as write_file:
        json.dump(all_programs_info, write_file, indent=4)

    #Simply printing the resultant output    
    print(json.dumps(all_programs_info))
        

    


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
res=get_list_of_programs(driver,[])#Calling this function to get names and URLs of all programs
get_concepts_covered(driver,res)#Calling this function to get information of each program and storing the output in output.json file 
driver.quit()

