import math,constants,config_local as config
from typing import List
import time
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import re

from selenium.webdriver.firefox.options import Options

def browserOptions():
    options = Options()
    firefoxProfileRootDir = config.firefoxProfileRootDir
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-gpu')
    if(config.headless):
        options.add_argument("--headless")

    options.add_argument("--disable-blink-features")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    options.add_argument("-profile")
    options.add_argument(firefoxProfileRootDir)

    return options

def prRed(prt):
    print(f"\033[91m{prt}\033[00m")

def prGreen(prt):
    print(f"\033[92m{prt}\033[00m")

def prYellow(prt):
    print(f"\033[93m{prt}\033[00m")

def getUrlDataFile():
    urlData = ""
    try:
        file = open('data/urlData.txt', 'r')
        urlData = file.readlines()
    except FileNotFoundError:
        text = "FileNotFound:urlData.txt file is not found. Please run ./data folder exists and check config.py values of yours. Then run the bot again"
        prRed(text)
    return urlData

def jobsToPages(numOfJobs: str) -> int:
  number_of_pages = 1

  if (' ' in numOfJobs):
    spaceIndex = numOfJobs.index(' ')
    totalJobs = (numOfJobs[0:spaceIndex])
    totalJobs_int = int(totalJobs.replace(',', ''))
    number_of_pages = math.ceil(totalJobs_int/constants.jobsPerPage)
    if (number_of_pages > 40 ): number_of_pages = 40

  else:
      number_of_pages = int(numOfJobs)

  return number_of_pages

def urlToKeywords(url: str) -> List[str]:
    keywordUrl = url[url.index("keywords=")+9:]
    keyword = keywordUrl[0:keywordUrl.index("&") ] 
    locationUrl =  url[url.index("location=")+9:]
    location = locationUrl[0:locationUrl.index("&") ] 
    return [keyword,location]

def writeResults(text: str):
    timeStr = time.strftime("%Y%m%d")
    fileName = "Applied Jobs DATA - " +timeStr + ".txt"
    try:
        with open("data/" +fileName, encoding="utf-8" ) as file:
            lines = []
            for line in file:
                if "----" not in line:
                    lines.append(line)
                
        with open("data/" +fileName, 'w' ,encoding="utf-8") as f:
            f.write("---- Applied Jobs Data ---- created at: " +timeStr+ "\n" )
            f.write("---- Number | Job Title | Company | Location | Work Place | Posted Date | Applications | Result "   +"\n" )
            for line in lines: 
                f.write(line)
            f.write(text+ "\n")
            
    except:
        with open("data/" +fileName, 'w', encoding="utf-8") as f:
            f.write("---- Applied Jobs Data ---- created at: " +timeStr+ "\n" )
            f.write("---- Number | Job Title | Company | Location | Work Place | Posted Date | Applications | Result "   +"\n" )

            f.write(text+ "\n")

def printInfoMes(bot:str):
    prYellow("ℹ️ " +bot+ " is starting soon... ")

def donate(self):
    prYellow('If you like the project, please support me so that i can make more such projects, thanks!')
    try:
        self.driver.get('https://commerce.coinbase.com/checkout/576ee011-ba40-47d5-9672-ef7ad29b1e6c')
    except Exception as e:
        prRed("Error in donate: " +str(e))

class LinkedinUrlGenerate:
    def generateUrlLinks(self):
        path = []
        for location in config.location:
            for keyword in config.keywords:
                    url = constants.linkJobUrl + "?f_AL=true&keywords=" +keyword+self.jobType()+self.remote()+self.checkJobLocation(location)+self.jobExp()+self.datePosted()+self.sortBy()
                    path.append(url)
        return path

    def checkJobLocation(self,job):
        jobLoc = "&location=" +job
        match job.casefold():
            case "asia":
                jobLoc += "&geoId=102393603"
            case "europe":
                jobLoc += "&geoId=100506914"
            case "northamerica":
                jobLoc += "&geoId=102221843&"
            case "southamerica":
                jobLoc +=  "&geoId=104514572"
            case "australia":
                jobLoc +=  "&geoId=101452733"
            case "africa":
                jobLoc += "&geoId=103537801"

        return jobLoc

    def jobExp(self):
        jobtExpArray = config.experienceLevels
        firstJobExp = jobtExpArray[0]
        jobExp = ""
        match firstJobExp:
            case "Internship":
                jobExp = "&f_E=1"
            case "Entry level":
                jobExp = "&f_E=2"
            case "Associate":
                jobExp = "&f_E=3"
            case "Mid-Senior level":
                jobExp = "&f_E=4"
            case "Director":
                jobExp = "&f_E=5"
            case "Executive":
                jobExp = "&f_E=6"
        for index in range (1,len(jobtExpArray)):
            match jobtExpArray[index]:
                case "Internship":
                    jobExp += "%2C1"
                case "Entry level":
                    jobExp +="%2C2"
                case "Associate":
                    jobExp +="%2C3"
                case "Mid-Senior level":
                    jobExp += "%2C4"
                case "Director":
                    jobExp += "%2C5"
                case "Executive":
                    jobExp  +="%2C6"

        return jobExp

    def datePosted(self):
        datePosted = ""
        match config.datePosted[0]:
            case "Any Time":
                datePosted = ""
            case "Past Month":
                datePosted = "&f_TPR=r2592000&"
            case "Past Week":
                datePosted = "&f_TPR=r604800&"
            case "Past 24 hours":
                datePosted = "&f_TPR=r86400&"
        return datePosted

    def jobType(self):
        jobTypeArray = config.jobType
        firstjobType = jobTypeArray[0]
        jobType = ""
        match firstjobType:
            case "Full-time":
                jobType = "&f_JT=F"
            case "Part-time":
                jobType = "&f_JT=P"
            case "Contract":
                jobType = "&f_JT=C"
            case "Temporary":
                jobType = "&f_JT=T"
            case "Volunteer":
                jobType = "&f_JT=V"
            case "Intership":
                jobType = "&f_JT=I"
            case "Other":
                jobType = "&f_JT=O"
        for index in range (1,len(jobTypeArray)):
            match jobTypeArray[index]:
                case "Full-time":
                    jobType += "%2CF"
                case "Part-time":
                    jobType +="%2CP"
                case "Contract":
                    jobType +="%2CC"
                case "Temporary":
                    jobType += "%2CT"
                case "Volunteer":
                    jobType += "%2CV"
                case "Intership":
                    jobType  +="%2CI"
                case "Other":
                    jobType  +="%2CO"
        jobType += "&"
        return jobType

    def remote(self):
        remoteArray = config.remote
        firstJobRemote = remoteArray[0]
        jobRemote = ""
        match firstJobRemote:
            case "On-site":
                jobRemote = "f_WT=1"
            case "Remote":
                jobRemote = "f_WT=2"
            case "Hybrid":
                jobRemote = "f_WT=3"
        for index in range (1,len(remoteArray)):
            match remoteArray[index]:
                case "On-site":
                    jobRemote += "%2C1"
                case "Remote":
                    jobRemote += "%2C2"
                case "Hybrid":
                    jobRemote += "%2C3"

        return jobRemote

    def salary(self):
        salary = ""
        match config.salary[0]:
            case "$40,000+":
                salary = "f_SB2=1&"
            case "$60,000+":
                salary = "f_SB2=2&"
            case "$80,000+":
                salary = "f_SB2=3&"
            case "$100,000+":
                salary = "f_SB2=4&"
            case "$120,000+":
                salary = "f_SB2=5&"
            case "$140,000+":
                salary = "f_SB2=6&"
            case "$160,000+":
                salary = "f_SB2=7&"    
            case "$180,000+":
                salary = "f_SB2=8&"    
            case "$200,000+":
                salary = "f_SB2=9&"                  
        return salary

    def sortBy(self):
        sortBy = ""
        match config.sort[0]:
            case "Recent":
                sortBy = "sortBy=DD"
            case "Relevent":
                sortBy = "sortBy=R"                
        return sortBy

# SELENIUM UTILS
def wait_until_visible_and_find(driver, ByLocal, locator_value, timeout=constants.botSpeed):
    """
    Waits until an element becomes clickable, then finds a new element using the same locator.
    :param driver: WebDriver instance
    :param locator_type: type of locator (e.g., "xpath", "id", "name", etc.)
    :param locator_value: value of the locator (e.g., "//div[@id='example']", "my_element", etc.)
    :param timeout: maximum time to wait for the element to become clickable (default is 10 seconds)
    :return: the new element found, or None if the element is not found within the timeout
    """
    try:
        wait = WebDriverWait(driver, timeout)
        new_element = wait.until(EC.visibility_of_element_located((ByLocal, locator_value)))
        return new_element
    except Exception as e:
        raise Exception(f"Timeout excedido ao tentar encontrar elemento {locator_value}.") from e

def wait_until_clickable_and_find(driver, ByLocal, locator_value, timeout=constants.botSpeed):
    """
    Waits until an element becomes clickable, then finds a new element using the same locator.
    :param driver: WebDriver instance
    :param locator_type: type of locator (e.g., "xpath", "id", "name", etc.)
    :param locator_value: value of the locator (e.g., "//div[@id='example']", "my_element", etc.)
    :param timeout: maximum time to wait for the element to become clickable (default is 10 seconds)
    :return: the new element found, or None if the element is not found within the timeout
    """
    try:
        wait = WebDriverWait(driver, timeout)
        new_element = wait.until(EC.element_to_be_clickable((ByLocal, locator_value)))
        return new_element
    except Exception as e:
        raise Exception(f"Timeout excedido ao tentar encontrar elemento {locator_value}.") from e

def wait_until_invisible_and_find(driver, ByLocal, locator_value, timeout=constants.botSpeed):
    """
    Waits until an element becomes clickable, then finds a new element using the same locator.
    :param driver: WebDriver instance
    :param locator_type: type of locator (e.g., "xpath", "id", "name", etc.)
    :param locator_value: value of the locator (e.g., "//div[@id='example']", "my_element", etc.)
    :param timeout: maximum time to wait for the element to become clickable (default is 10 seconds)
    :return: the new element found, or None if the element is not found within the timeout
    """
    try:
        wait = WebDriverWait(driver, timeout)
        new_element = wait.until(EC.invisibility_of_element_located((ByLocal, locator_value)))
        return new_element
    except Exception as e:
        raise Exception(f"Timeout excedido ao tentar encontrar elemento {locator_value}.") from e

def wait_until_visible_and_find_all(driver, ByLocal, locator_value, timeout=constants.botSpeed):
    """
    Waits until an element becomes clickable, then finds a new element using the same locator.
    :param driver: WebDriver instance
    :param locator_type: type of locator (e.g., "xpath", "id", "name", etc.)
    :param locator_value: value of the locator (e.g., "//div[@id='example']", "my_element", etc.)
    :param timeout: maximum time to wait for the element to become clickable (default is 10 seconds)
    :return: the new element found, or None if the element is not found within the timeout
    """
    try:
        wait = WebDriverWait(driver, timeout)
        new_element = wait.until(EC.visibility_of_all_elements_located((ByLocal, locator_value)))
        return new_element
    except Exception as e:
        raise Exception(f"Timeout excedido ao tentar encontrar elemento {locator_value}.") from e

def wait_until_visible_and_find_multiple_locators_parallel(driver, ByAndLocatorDictArray, timeout=constants.botSpeed):
    """
    Waits until an element becomes clickable, then finds a new element using the same locator.
    :param driver: WebDriver instance
    :param ByAndLocatorDict: dictionary with the locator type as key and the locator value as value
    :param timeout: maximum time to wait for the element to become clickable (default is 10 seconds)
    :return: the new element found, or None if the element is not found within the timeout
    """
    new_elements = []
    with ThreadPoolExecutor() as executor:
        args_for_map = [(driver, ByAndLocatorDict, timeout) for ByAndLocatorDict in ByAndLocatorDictArray]
        results = executor.map(wait_visibility, args_for_map)
        new_elements = list(results)
    # args_for_map = [(driver, ByAndLocatorDict, timeout) for ByAndLocatorDict in ByAndLocatorDictArray]
    # new_elements = []
    # for args in args_for_map:
    #     new_elements.append(wait_visibility(args))
    return new_elements

def wait_visibility(args):
    driver, ByAndLocatorDict, timeout = args
    wait = WebDriverWait(driver, timeout=constants.botSpeed)
    result = False
    by = ByAndLocatorDict["By"]
    locator_value = ByAndLocatorDict["locator_value"]
    try:
        result = wait.until(EC.visibility_of_all_elements_located((by, locator_value)))
    except:
        _foo = None
    return result

def find_child_element_s(parent_element, ByLocal, locator_value, multiple = False):
    """
    Finds child elements of a given element.
    :param parent_element: the parent element
    :param locator_type: type of locator (e.g., "xpath", "id", "name", etc.)
    :param locator_value: value of the locator (e.g., "//div[@id='example']", "my_element", etc.)
    :return: the child elements found, or None if the element is not found
    """
    try:
        if not parent_element.is_displayed():
            raise Exception(f"{parent_element}")
        if multiple:
            elements = parent_element.find_elements(ByLocal, locator_value)
            return elements
        else:
            return parent_element.find_element(ByLocal, locator_value)
    except Exception as e:
        raise Exception(f"Elemento não existe mais: {parent_element}") from e

def elementCanBeFound(driver, ByLocal, locator_value):
    try:
        driver.find_element(ByLocal, locator_value)
        return True
    except:
        return False

def ifException_False(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return False
    return wrapper

def storeUnansweredJson(fileName, error):
    #Change properties with label in the name to just 'Label'
    newError = {}
    for key in error:
        if 'label' in key.lower():
            newError['Label'] = error[key]
        else:
            newError[key] = error[key]
    #Check for duplicates only if the file exists
    try:
        with open(f'data/unanswered{fileName}.json', 'r', encoding="utf-8") as json_file:
            for line in json_file:
                if newError == json.loads(line):
                    return
    except Exception as e:
        pass

    #Save the data
    with open(f'data/unanswered{fileName}.json', 'a', encoding="utf-8") as json_file:
        json_file.write(json.dumps(newError, ensure_ascii=False) + "\n")

def storeUnansweredData(errorsList):
    for error in errorsList:
        if 'Radio Label' in error:
            storeUnansweredJson('RadioLabels', error)
        elif 'Text Label' in error:
            storeUnansweredJson('TextLabels', error)
        elif 'Select Label' in error:
            storeUnansweredJson('SelectLabels', error)
        elif 'Checkbox Label' in error:
            storeUnansweredJson('CheckboxLabels', error)
    
    # TODO log that the errors were stored in the file
    # TODO log errors that were not stored in the file

def getErrorsListFromJson():
    errorsList = []
    files = ['RadioLabels', 'TextLabels', 'SelectLabels', 'CheckboxLabels']
    for fileName in files:
        try:
            with open(f'data/unanswered{fileName}.json', 'r', encoding="utf-8") as json_file:
                for line in json_file:
                    with open('data/answeredQuestions.json', 'r', encoding="utf-8") as answered_file:
                        linha = json.loads(line)
                        if not getAnsweredQuestion(linha['Label']):
                            if "ncia de pelo menos 2 anos com gestão de times de desenvolvimento" in line:
                                a = None
                            errorsList.append(linha)
        except:
            pass
    # try:
    #     with open('data/unansweredRadioLabels.json', 'r', encoding="utf-8") as json_file:
    #         for line in json_file:
    #             with open('data/answeredQuestions.json', 'r', encoding="utf-8") as answered_file:
    #                 if not getAnsweredQuestion(json.loads(line)['Label']):
    #                     if "ncia de pelo menos 2 anos com gestão de times de desenvolvimento" in line:
    #                         a = None
    #                     errorsList.append(json.loads(line))
    # except:
    #     pass
    # try:
    #     with open('data/unansweredTextLabels.json', 'r', encoding="utf-8") as json_file:
    #         for line in json_file:
    #             with open('data/answeredQuestions.json', 'r', encoding="utf-8") as answered_file:
    #                 if not getAnsweredQuestion(json.loads(line)['Label']):
    #                     if "ncia de pelo menos 2 anos com gestão de times de desenvolvimento" in line:
    #                         a = None
    #                     errorsList.append(json.loads(line))
    # except:
    #     pass
    # try:    
    #     with open('data/unansweredSelectLabels.json', 'r', encoding="utf-8") as json_file:
    #         for line in json_file:
    #             with open('data/answeredQuestions.json', 'r', encoding="utf-8") as answered_file:
    #                 if getAnsweredQuestion(json.loads(line)['Label']):
    #                     continue
    #             errorsList.append(json.loads(line))
    # except:
    #     pass
    # try:    
    #     with open('data/unansweredCheckboxLabels.json', 'r', encoding="utf-8") as json_file:
    #         for line in json_file:
    #             # with open('data/answeredQuestions.json', 'r', encoding="utf-8") as answered_file:
    #             #     if getAnsweredQuestion(json.loads(line)['Label']):
    #             #         continue
    #             errorsList.append(json.loads(line))
    # except:
    #     pass
    return errorsList

def saveAnsweredQuestions(QuestionAnswer_List: List[dict]):
    with open('data/answeredQuestions.json', 'a', encoding="utf-8") as json_file:
        for questionAnswer in QuestionAnswer_List:
            json_file.write(json.dumps(questionAnswer, ensure_ascii=False) + "\n")

def saveAnsweredQuestion(QuestionAnswer: dict):
    with open('data/answeredQuestions.json', 'a', encoding="utf-8") as json_file:
        json_file.write(json.dumps(QuestionAnswer, ensure_ascii=False) + "\n")

def getAnsweredQuestion(label: str):
    try:
        with open('data/answeredQuestions.json', 'r', encoding="utf-8") as json_file:
            for line in json_file:
                line = line.replace("\n", "")
                line = PadronizeSpaces(line)
                label = PadronizeSpaces(label)
                answerDict = json.loads(line)
                for dictLabel in answerDict:
                    if label in dictLabel:
                        return json.loads(line)
    except:
        pass
    
    return False

def getAnsweredQuestions():
    list = []
    with open('data/answeredQuestions.json', 'r', encoding="utf-8") as json_file:
        for line in json_file:
            list.append(json.loads(line))
    return list

def PadronizeSpaces(texto):
    # Remove extra spaces before and after commas
    texto = re.sub(r'\s*,\s*', ', ', texto)
    # Remove extra spaces before dot
    texto = re.sub(r'\s*\.', '.', texto)
    # Remove extra spaces
    texto = re.sub(r'\s+', ' ', texto)
    return texto