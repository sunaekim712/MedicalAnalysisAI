from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import os
import json
import re
from pandas.core.common import flatten
from typing import List
from typing import Dict
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI

from template import *


class MDCalc:
    def __init__(self):
        #chrome_options = Options()
        #chrome_options.add_experimental_option("detach", True)
        #options=chrome_options
        #self.driver = webdriver.Chrome(service=Service("chromedriver.exe"))
        #self.driver.get("https://www.mdcalc.com")
        self.driver=None
        self.index=0
        self.dict={}
        self.key={}
        self.length=0
        self.front_page_options=[]
        self.front_page_options_key=[]
        self.report=[]
        if os.path.isfile("front_page_options.json"):
            with open("front_page_options.json","r") as openfile:
                [self.front_page_options,self.front_page_options_key]=json.load(openfile)

        else:
            self.scrap_first_page()
    def scrap_first_page(self):
        driver1 = webdriver.Chrome(service=Service("chromedriver.exe"))
        driver1.get("https://www.mdcalc.com/#All")
        #button=driver.find_elements(By.CLASS_NAME,"Home_svg-icon__391el")
        #button[5].click()
        array=driver1.find_elements(By.CLASS_NAME,"calculatorRow_row-container__HM_dC")
        options=[]
        counter=0
        for selected in array:
            top=selected.find_element(By.CLASS_NAME,"calculatorRow_row-top__GXs4V")
            bottom=selected.find_element(By.CLASS_NAME,"calculatorRow_row-bottom__6dGGF")
            self.front_page_options.append("Option#"+str(counter)+":"+(top.text).replace("\n", "")+"("+(bottom.text).replace("\n", "")+")")
            #self.front_page_options.append("Option#"+str(counter)+":"+(top.text).replace("\n", ""))
            #self.front_page_options.append("Option#"+str(counter)+":"+selected.text)
            self.front_page_options_key.append(selected.find_element(By.TAG_NAME,'a').get_attribute("href"))
            counter=counter+1
        with open("front_page_options.json","w") as writefile:
            json.dump([self.front_page_options,self.front_page_options_key],writefile,indent=2)
        #return self.front_page_options
   

    def scrap_form(self,option_number,index=None):
        current_url=self.driver.current_url
        if current_url!=self.front_page_options_key[option_number]:
            self.driver.get(self.front_page_options_key[option_number])
        #print(self.front_page_options[option_number])

        subheading_text=""
        element_array=[]
        raw_array=self.driver.find_elements(By.XPATH,"//*[@class='calc_input-wrapper__LavoA calc_hint__zfosT' or @class='calc_input-wrapper__LavoA calc_field__E4TVx']")
        for element in raw_array:
            if len(element.find_elements(By.CLASS_NAME,"calc_subheading__GV4TJ"))!=0:
                subheading_text=element.find_elements(By.CLASS_NAME,"calc_subheading__GV4TJ")[0].text
            elif len(element.find_elements(By.CLASS_NAME,"calc_subheading-diagnostic__0bWGy"))!=0:
                subheading_text=element.find_elements(By.CLASS_NAME,"calc_subheading-diagnostic__0bWGy")[0].text 
            if len(element.find_elements(By.CLASS_NAME,"calc_side-by-side__F4M_M"))!=0:
                element_array.append([element.find_element(By.CLASS_NAME,"calc_side-by-side__F4M_M"),subheading_text])
            elif len(element.find_elements(By.CLASS_NAME,"calc_input-diagnostic_criteria__JylNJ"))!=0:
                element_array.append([element.find_element(By.CLASS_NAME,"calc_input-diagnostic_criteria__JylNJ"),subheading_text])

        #array=self.driver.find_elements(By.CLASS_NAME,"calc_side-by-side__F4M_M")
        array=element_array
        self.length=len(array)
        if index!=None:
            local_index=index
        else:
            local_index=self.index
        if local_index<=self.length-1:
            selected=array[local_index][0]
            subheading_of_selected=array[local_index][1]
            if index==None:
                self.index=self.index+1
            
            selected_array=selected.find_elements(By.CLASS_NAME,"calc_btn-default__qwVkK")
            selected_input=selected.find_elements(By.CLASS_NAME,"calc_textbox-input__sd0Ap")
            selected_checker_array=selected.find_elements(By.CLASS_NAME,"calc_input-title-diagnostic__PeS_F")
            if len(selected_input)!=0:
                selected_label=selected.find_element(By.CLASS_NAME,"calc_input-name-label__hgiue").text
                input1=selected.find_element(By.CLASS_NAME,"calc_textbox-input__sd0Ap")
                if len(selected.find_elements(By.CLASS_NAME,"calc_unit-button-mute__dQEge"))==0:
                    element_name="calc_unit-button__uyVZn"
                    beside_input1=selected.find_element(By.CLASS_NAME,"calc_unit-button__uyVZn")
                else:
                    element_name="calc_unit-button-mute__dQEge"
                    beside_input1=selected.find_element(By.CLASS_NAME,"calc_unit-button-mute__dQEge")
                #input1.send_keys("Selenium")
                #print(beside_input1.text)
                #print(selected_label+"("+beside_input1.text+"): ")
                self.dict[selected_label+"("+beside_input1.text+")"]=""
                self.key[selected_label+"("+beside_input1.text+")"]={"type":"input_field","subheading":subheading_of_selected,"element":input1}
                return {"subheading":subheading_of_selected,"form":{selected_label+"("+beside_input1.text+")":""}}
            elif len(selected_array)!=0:
                # unchecked_buttons=selected.find_elements(By.CLASS_NAME,"calc_btn-default__qwVkK")
                # checked_buttons=selected.find_elements(By.CLASS_NAME,"calc_btn-selected__bTkck")
                # #print(selected_label+":"+"/".join([page.text for page in selected_array]))                                                                         
                # self.dict[selected_label]="/".join([page.text for page in checked_buttons]+[page.text for page in unchecked_buttons])
                # self.key[selected_label]={"type":"button","element":{}}
                # if len(checked_buttons)!=0:
                #     for element1 in checked_buttons:
                #         self.key[selected_label]["element"][element1.text]={"type":"checked_button","element":element1}
                # if len(unchecked_buttons)!=0:
                #     for element2 in unchecked_buttons:
                #         self.key[selected_label]["element"][element2.text]={"type":"unchecked_button","element":element2}
                selected_label=selected.find_element(By.CLASS_NAME,"calc_input-name-label__hgiue").text
                def get_text(button1):
                    fazool_text_container=button1.find_elements(By.CLASS_NAME,"calc_input-toggle-group-point__TrOXe")
                    if len(fazool_text_container)==0:
                        fazool_text_container=button1.find_elements(By.CLASS_NAME,"calc_input-toggle-point__b5cDj")
                    if len(fazool_text_container)!=0:
                        #return button1.text.replace(fazool_text_container[0].text,"").replace("\n","")
                        #button1.text.replace(fazool_text_container[0].text,"").replace("\n","")
                        return re.sub(r'\n$','',re.sub(re.compile(re.escape(fazool_text_container[0].text) + '$'),'',button1.text))
                    else:
                        return re.sub(r'\n$','',button1.text)
                unchecked_buttons=selected.find_elements(By.CLASS_NAME,"calc_btn-default__qwVkK")
                checked_buttons=selected.find_elements(By.CLASS_NAME,"calc_btn-selected__bTkck")
                #print(selected_label+":"+"/".join([page.text for page in selected_array]))                                                                         
                self.dict[selected_label]="/".join([get_text(button) for button in checked_buttons]+[get_text(button) for button in unchecked_buttons])
                self.key[selected_label]={"type":"button","subheading":subheading_of_selected,"element":{}}
                if len(checked_buttons)!=0:
                    for element1 in checked_buttons:
                        self.key[selected_label]["element"][get_text(element1)]={"type":"checked_button","element":element1}
                if len(unchecked_buttons)!=0:
                    for element2 in unchecked_buttons:
                        self.key[selected_label]["element"][get_text(element2)]={"type":"unchecked_button","element":element2}
                
                return {"subheading":subheading_of_selected,"form":{selected_label:"/".join([get_text(page) for page in checked_buttons]+[get_text(page) for page in unchecked_buttons])}}
            elif len(selected_checker_array)!=0:
                self.dict[selected_checker_array[0].text]="check/uncheck"
                self.key[selected_checker_array[0].text]={"type":"checkbox","subheading":subheading_of_selected,"element":selected_checker_array[0]}
                return {"subheading":subheading_of_selected,"form":{selected_checker_array[0].text:"check/uncheck"}}

        else:
            return None

    def write(self,dict1):
        for labels in dict1.keys():
            if self.key[labels]['type']=='button':
                if self.key[labels]['element'][dict1[labels]]['type']=="unchecked_button":
                    element=self.key[labels]['element'][dict1[labels]]['element']
                    #element.click()
                    self.driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
                    self.driver.execute_script("arguments[0].click();", element)

                elif self.key[labels]['element'][dict1[labels]]['type']=="checked_button":
                    element=self.key[labels]['element'][dict1[labels]]['element']
                    self.driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
                    self.driver.execute_script("arguments[0]", element)
            elif self.key[labels]['type']=='input_field':
                element=self.key[labels]['element']
                
                element.clear()
                self.driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
                element.send_keys(dict1[labels])
            elif self.key[labels]['type']=="checkbox":
                state_of_checkbox=self.key[labels]["element"].find_elements(By.CLASS_NAME,"calc_input-checkbox-default__aYpuT")[0].is_selected()
                element=self.key[labels]["element"]
                if dict1[labels]=="check"and state_of_checkbox==False:
                    self.driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
                    self.driver.execute_script("arguments[0].click();", element)
                elif dict1[labels]=="uncheck" and state_of_checkbox==True:
                    self.driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
                    self.driver.execute_script("arguments[0].click();", element)
                else:
                    self.driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)

        #from selenium.webdriver.support.wait import WebDriverWait
        #wait = WebDriverWait(driver, timeout=2000)
        #wait.until(lambda d : driver.find_element(By.CLASS_NAME,"calc_result-list__UKb1J").is_displayed())
        #return driver.find_element(By.CLASS_NAME,"calc_result-list__UKb1J").text

    def choose(self,information,model=3):
        def split(options_list,size):
            start = 0
            end = len(options_list)
            master_array=[]
            for i in range(start, end, size): 
                x = i 
                master_array.append(options_list[x:x+size])
            return master_array

        class Options(BaseModel):
            option_list: List[int] = Field(description="list of option#")
        
        parser = PydanticOutputParser(pydantic_object=Options)
        prompt=PromptTemplate.from_template(template1+template2+template3)
        llm3 = ChatOpenAI(temperature=0,model_name="gpt-3.5-turbo")
        chain3=prompt|llm3|parser
        llm4 = ChatOpenAI(temperature=0,model_name="gpt-4-turbo")
        chain4=prompt|llm4|parser
        options=self.front_page_options
        counter=0
        previous_option_list={}
        print("Selecting Options from first page")
        while True:
            list1=[]
            list2=[]
            for element in split(options,100):
                if model==3:
                    option=chain3.invoke({'Information':information,"Options":element,"format_instructions":parser.get_format_instructions()})
                elif model==4:
                    option=chain4.invoke({'Information':information,"Options":element,"format_instructions":parser.get_format_instructions()})
                if len(option.option_list)!=0:
                    list1.append(option.option_list)
            list1=list(flatten(list1))
            for i in list1:
                list2.append(self.front_page_options[i])
            options=list2
            if previous_option_list==set(list1):
                break
            else:
                previous_option_list=set(list1)
            """if len(options)<=5:
                            break"""
            #print(counter)
            counter=counter+1
        #print(options)
        return list1

    def fill_form(self,option_num=652,information=None,model=3):
        class Form(BaseModel):
            form: Dict = Field(description="filled form according to information provided.Reproduce the key of form dictionary exactly as it is")
            #reason:str=Field(description="give reason how/why the filled form is filled the way it is")
        parser_form = PydanticOutputParser(pydantic_object=Form)
        prompt_form=PromptTemplate.from_template(template4+template3)
        llm3 = ChatOpenAI(temperature=0,model_name="gpt-3.5-turbo")
        chain3_form=prompt_form|llm3|parser_form
        llm4 = ChatOpenAI(temperature=0,model_name="gpt-4-turbo")
        chain4_form=prompt_form|llm4|parser_form
        self.index=0
        self.dict={}
        self.key={}
        self.length=0
        #counter=0
        whole_form={}
        #whole_form_with_reason=[]
        print("Filled Form:")
        while True:
            scrapped_form_result=self.scrap_form(option_number=option_num)
            #print([subheading_text,scrapped_form])
            if scrapped_form_result==None:
                wait = WebDriverWait(self.driver, timeout=30)
                wait.until(lambda d : self.driver.find_element(By.CLASS_NAME,"calc_result-list__UKb1J").is_displayed())
                result1=self.driver.find_element(By.CLASS_NAME,"calc_result-list__UKb1J").text
                break
            subheading_text=scrapped_form_result["subheading"]
            scrapped_form=scrapped_form_result["form"]
            if model==3:
                form=chain3_form.invoke({'Information':information,"Option":self.front_page_options[option_num],"subheading":subheading_text,"form":scrapped_form,"format_instructions":parser_form.get_format_instructions()})
            elif model==4:
                form=chain4_form.invoke({'Information':information,"Option":self.front_page_options[option_num],"subheading":subheading_text,"form":scrapped_form,"format_instructions":parser_form.get_format_instructions()})
            self.write(form.form)
            whole_form.update(form.form)
            #print("["+form.form+"]")
            for key in form.form:
                print("[",key,":",form.form[key],"]")
            #whole_form_with_reason.append([form.form,form.reason])
            #print("Filled entry#"+str(counter)+" of form")
            #counter=counter+1
        #print("Result:")
        #print(result1)
        Result={"information":information,"Selected_Option":self.front_page_options[option_num],"filled_form":whole_form,"result":result1}#"whole_form_with_reason":whole_form_with_reason
        self.report.append(Result)
        return Result

    def verify(self,information):
        #chrome_options = Options()
        #chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(service=Service("chromedriver.exe"))#options=chrome_options
        self.driver.get("https://www.mdcalc.com/#All")
        option_list=self.choose(information=information,model=4)
        for option in option_list:
            print("Selected Option:")
            print(self.front_page_options[option],"\n")
            result=self.fill_form(option_num=option,information=information,model=4)
            print("\nResult:")
            print(result["result"])
            print("---------------------------------------------------")
            print("\n")

        self.driver.quit()


    def form_fill(self,information,option_number=None,MODEL=4):
        #chrome_options = Options()
        #chrome_options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(service=Service("chromedriver.exe"))#,options=chrome_options)
        #self.driver.get("https://www.mdcalc.com/#All")
        print("Selected Option:")
        print(self.front_page_options[option_number],"\n")
        result=self.fill_form(option_num=option_number,information=information,model=MODEL)
        print("\nResult:")
        print(result["result"])
        print("---------------------------------------------------")
        print("\n")
        self.driver.quit()

    