import datetime
import json
import math
import os
import platform
import random
import time
import traceback
from concurrent.futures import ThreadPoolExecutor

import selenium.webdriver.support.expected_conditions as EC
from langdetect import detect
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import config_local
import constants
import finders
import utils
from utils import prGreen, prRed, prYellow


class Linkedin:

    def __init__(self):
        self.driver = self.startDriver(True)
        self.JobIDS = {
            "Applied Jobs": [],
            "Skipped Jobs": [],
            "Blacklisted Jobs": [],
            "Error Jobs": [],
        }

    def startDriver(self, kills = False):
        browser = config_local.browser[0].lower()
        linkedinEmail = config_local.email
        if kills:
            os.system("taskkill /im geckodriver.exe /f")
            os.system("taskkill /im firefox.exe /f")
        if browser == "firefox":
            if len(linkedinEmail) > 0:
                if platform.system == "Linux" and config_local.firefoxProfileRootDir == "":
                    prYellow(
                        "On Linux you need to define profile path to run the bot with Firefox. Go about:profiles find root directory of your profile paste in line 8 of config file next to firefoxProfileRootDir "
                    )
                    exit()
                else:
                    driver = webdriver.Firefox()
                    self.login(driver)
            else:
                driver = webdriver.Firefox(options=utils.browserOptions())
        elif browser == "chrome":
            driver = webdriver.Chrome(ChromeDriverManager().install())
            self.login(driver)
            
        return driver;

    def login(self, driver):
        driver.get(
                "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin"
            )
        prYellow("Trying to log in linkedin.")
        try:
            utils.wait_until_visible_and_find(driver,"id",
                                      "username").send_keys(config_local.email)
            utils.wait_until_visible_and_find(driver,"id", "password").send_keys(
                config_local.password)
            utils.wait_until_visible_and_find(driver,
                "xpath",
                '//*[@id="organic-div"]/form/div[3]/button').click()
        except:
            prRed(e)

    def generateUrls(self):
        if not os.path.exists("data"):
            os.makedirs("data")
        try:
            with open("data/urlData.txt", "w", encoding="utf-8") as file:
                linkedinJobLinks = utils.LinkedinUrlGenerate().generateUrlLinks()
                for url in linkedinJobLinks:
                    file.write(url + "\n")
            prGreen("Urls are created successfully, now the bot will visit those urls.")
        except:
            prRed(
                "Couldnt generate url, make sure you have /data folder and modified config_local.py file for your preferances."
            )
    
    def go_through_offers(self, jobID, countApplied, countJobs):
        # need to get a better page
        start_time = datetime.datetime.now()
        offerPage = "https://www.linkedin.com/jobs/view/" + \
            str(jobID)

        while True:
            self.driver.get(offerPage)
            try:
                if utils.wait_until_visible_and_find(self.driver, By.XPATH, "//*[contains(@class,'jobs-post-job')]") is not False:
                    break
            except:
                prRed("Error in going through offers: " + str(e))

        countJobs += 1

        jobProperties = self.getJobProperties(countJobs)
        button = self.easyApplyButton()
        for blacklistword in config_local.blacklist:
            if blacklistword in jobProperties:
                self.saveJobId(jobID, "Blacklisted Jobs")
                print(
                    "Blacklisted word found in url - skipping (" +
                    blacklistword + ")")
                button = False
                return countApplied, countJobs
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        print("Time to get job properties and button: " + str(time_diff))
        description = self.driver.find_element(
            By.XPATH,
            "//article[contains(@class, 'jobs-description')]/div"
        ).get_attribute("innerText")
        # To filter by language choose abbreviations here: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        # if detect(description) != "en":
        #     lineToWrite = (jobProperties + " | " +
        #                     "* 🌍 Non English Language Detected, Skipped: " +
        #                     str(offerPage))
        #     self.displayWriteResults(lineToWrite)
        if button is not False:
            try:
                button.click()
                utils.wait_until_visible_and_find(self.driver, By.XPATH, "//div/div[contains(@class, 'jobs-easy-apply-modal')]")
                countApplied += 1
                result = self.applyProcess(offerPage, jobID)
                lineToWrite = jobProperties + " | " + result
                self.displayWriteResults(lineToWrite)
            except Exception as e2:
                self.saveJobId(jobID, "Error Jobs")
                lineToWrite = (
                    jobProperties + " | " +
                    "* 🔴 Cannot apply to this Job! " +
                    str(offerPage))
                self.displayWriteResults(lineToWrite)
        else:
            self.saveJobId(jobID, "Skipped Jobs")
            lineToWrite = (jobProperties + " | " +
                            "* 🟡 Already applied or Error to acquire button! Job: " +
                            str(offerPage))
            self.displayWriteResults(lineToWrite)
        return countApplied, countJobs

    def linkJobApply(self):
        self.generateUrls()
        countApplied = 0
        countJobs = 0

        urlData = utils.getUrlDataFile()

        for url in urlData:
            self.driver.get(url)

            totalJobs = utils.wait_until_visible_and_find(self.driver,By.XPATH, "//small").text
            totalPages = utils.jobsToPages(totalJobs)

            urlWords = utils.urlToKeywords(url)
            lineToWrite = ("\n Category: " + urlWords[0] + ", Location: " +
                           urlWords[1] + ", Applying " + str(totalJobs) +
                           " jobs.")
            self.displayWriteResults(lineToWrite)

            for page in range(totalPages):
                currentPageJobs = constants.jobsPerPage * page
                url = url + "&start=" + str(currentPageJobs)
                self.driver.get(url)
                time.sleep(random.uniform(1, constants.botSpeed))

                try:
                    offersPerPage = utils.wait_until_visible_and_find_all(self.driver,
                        By.XPATH, "//li[@data-occludable-job-id]")
                except:
                    continue

                offerIds = []
                for offer in offersPerPage:
                    offerId = offer.get_attribute("data-occludable-job-id")
                    offerIds.append(int(offerId.split(":")[-1]))

                for jobID in offerIds:
                    # if self.checkJobId(jobID):
                    #     prYellow("💾 Job already visited: " + str(jobID))
                    #     continue
                    countApplied, countJobs = self.go_through_offers(jobID, countApplied, countJobs)

            prYellow("Category: " + urlWords[0] + "," + urlWords[1] +
                     " applied: " + str(countApplied) + " jobs out of " +
                     str(countJobs) + ".")

    def getJobProperties(self, count):
        textToWrite = ""
        jobTitle = ""
        jobCompany = ""
        jobLocation = ""
        jobWOrkPlace = ""
        jobPostedDate = ""
        jobApplications = ""

        try:
            jobTitle = (utils.wait_until_visible_and_find(self.driver,
                By.XPATH, "//h1[contains(@class, 'job-title')]").get_attribute(
                    "innerText").strip())
        except Exception as e:
            # prYellow("Warning in getting jobTitle: " + str(e)[0:50])
            jobTitle = ""
        try:
            jobCompany = self.driver.find_element(
                By.XPATH,
                "//a[contains(@class, 'ember-view') and contains(@class, 't-black')]",
            ).get_attribute("innerText").strip()
        except Exception as e:
            # prYellow("Warning in getting jobCompany: " + str(e)[0:50])
            jobCompany = ""
        try:
            jobLocation = self.driver.find_element(
                By.XPATH, "//span[contains(@class, 'bullet')]").get_attribute(
                    "innerText").strip()
        except Exception as e:
            # prYellow("Warning in getting jobLocation: " +str(e)[0:50])
            jobLocation = ""
        try:
            jobWOrkPlace = self.driver.find_element(
                By.XPATH,
                "//span[contains(@class, 'workplace-type')]").get_attribute(
                    "innerText").strip()
        except Exception as e:
            # prYellow("Warning in getting jobWorkPlace: " +str(e)[0:50])
            jobWOrkPlace = ""
        try:
            jobPostedDate = self.driver.find_element(
                By.XPATH,
                "//span[contains(@class, 'posted-date')]").get_attribute(
                    "innerText").strip()
        except Exception as e:
            # prYellow("Warning in getting jobPostedDate: " +str(e)[0:50])
            jobPostedDate = ""
        try:
            jobApplications = self.driver.find_element(
                By.XPATH,
                "//span[contains(@class, 'tvm__text tvm__text--neutral') and contains(text(), 'applicant')]",
            ).get_attribute("innerText").strip()
        except Exception as e:
            # prYellow("Warning in getting jobApplications: " + str(e)[0:50])
            jobApplications = ""

        textToWrite = (str(count) + " | " + jobTitle + " | " + jobCompany +
                       " | " + jobApplications)
        return textToWrite

    def easyApplyButton(self):
        try:
            while True:
                buttonFound = utils.ifException_False(utils.wait_until_visible_and_find)(self.driver, By.XPATH, '//div[contains(@class, "jobs-apply-button--top-card")]//span[contains(normalize-space(), "Easy Apply")]/parent::button')
                clickableButtonFound = utils.ifException_False(utils.wait_until_clickable_and_find)(self.driver, By.XPATH, '//div[contains(@class, "jobs-apply-button--top-card")]//span[contains(normalize-space(), "Easy Apply")]/parent::button')
                if buttonFound is False:
                    return False
                if buttonFound is not False and clickableButtonFound is not False:
                    return clickableButtonFound
                if buttonFound is not False and clickableButtonFound is False:
                    self.driver.refresh()
        except Exception as e:
            print(e)
            prRed("Error in easyApplyButton")
            return False


    def submitFound(self, errorslist):
        try:
            while not utils.elementCanBeFound(self.driver, By.XPATH, '//*[contains(@class, "artdeco-inline-feedback__message")]'):
                button = None
                try:
                    button = self.driver.find_element(By.XPATH, "//div/div[contains(@class, 'jobs-easy-apply-modal')]//button[contains(normalize-space(), 'Next')]")
                except:
                    try:
                        button = self.driver.find_element(By.XPATH, "//div/div[contains(@class, 'jobs-easy-apply-modal')]//button[contains(normalize-space(), 'Review')]")
                    except:
                        try:
                            button = self.driver.find_element(By.XPATH, "//div/div[contains(@class, 'jobs-easy-apply-modal')]//button[contains(normalize-space(), 'Submit')]")
                            if config_local.followCompanies is False:
                                try:
                                    self.driver.find_element(
                                        By.CSS_SELECTOR,
                                        "label[for='follow-company-checkbox']").click()
                                except:
                                    pass
                        except:
                            pass
                finders.continueNextStep([button], errorslist)
        except Exception as e:
            print(e)
            prRed("Error in submitFound")
        try:
            utils.wait_until_visible_and_find(self.driver, By.XPATH, "//h3[contains(normalize-space(), 'Your application was sent')]")
            return True
        except:
            prRed("Error in submitFound sent")
            return False

    def applyProcess(self, offerPage, JobId):
        result = ""
        progress = 0
        attempts = 0
        errorslist = []
        start_time = datetime.datetime.now()
        try:
            try:
                while self.submitFound(errorslist) == False and attempts < 1:
                    try:
                        barNow = utils.wait_until_visible_and_find(self.driver,
                            By.XPATH, "//progress").get_attribute("aria-valuenow")
                    except Exception as e:
                        print("Error in getting BAR: " + str(e))

                    if int(progress) == int(barNow):
                        attempts += 1
                    else:
                        attempts = 0
                        errorslist = []
                    progress = barNow
                    
                    finders.check_all_THEN_fill_all(self, config_local, errorslist)
            except Exception as e:
                print(e)
                prRed(f"Error applying page with {attempts} attempts")
                
            try:

                self.driver.find_element(
                    By.CSS_SELECTOR,
                    "button[aria-label='Submit application']").click()
            except:
                print(e)
                print("Error in submit application")

            self.driver.find_element(By.XPATH,
                "//h3[contains(normalize-space(), 'sent')]")


            self.saveJobId(JobId, "Applied Jobs")
            result = "* 🟢 Just Applied to this job: " + str(offerPage)
        except Exception as e:
            if len(errorslist) == 0:
                print(e)
                print("Error in applyProcess: " + str(e))
            self.saveJobId(JobId, "Error Jobs")
            result = (
                "* 🔴 " +
                " Couldn't apply to this job! Extra info needed. Link: "
                + str(offerPage) +
                "\n--------------------------- errorList -----------------------------\n"
                + str(errorslist) +
                "\n------------------------------------------------------------------\n"
            )
        end_time = datetime.datetime.now()
        time_diff = end_time - start_time
        print("Time to apply: " + str(time_diff))
        return result

    def displayWriteResults(self, lineToWrite: str):
        try:
            print(lineToWrite)
            utils.writeResults(lineToWrite)
        except Exception as e:
            prRed("Error in DisplayWriteResults: " + str(e))
    
    def saveJobIDS(self):
        try:
            previousData = json.loads(open("data/JobIDS.json", encoding="utf-8").read())
            for key in self.JobIDS:
                for job in self.JobIDS[key]:
                    if job not in previousData[key]:
                        previousData[key].append(job)
            with open("data/JobIDS.json", "w", encoding="utf--8") as file:
                json.dump(previousData, file, ensure_ascii=False)
                prGreen("JobIDS are saved successfully.")
        except Exception as e:
            prRed("Error in saveJobIDS: " + str(e))
    
    def saveJobId(self, JobId, key):
        try:
            previousData = json.loads(open("data/JobIDS.json", encoding="utf-8").read())
            if JobId not in previousData[key]:
                previousData[key].append(JobId)
            with open("data/JobIDS.json", "w", encoding="utf--8") as file:
                json.dump(previousData, file, ensure_ascii=False)
                prGreen("JobIDS are saved successfully.")
        except Exception as e:
            prRed("Error in saveJobId: " + str(e))
    
    def checkJobId(self, JobId):
        try:
            previousData = json.loads(open("data/JobIDS.json", encoding="utf-8").read())
            for key in previousData:
                if JobId in previousData[key]:
                    return True
            return False
        except Exception as e:
            prRed("Error in checkJobId: " + str(e))
            return False


start = time.time()
while True:
    try:
        linkedin = Linkedin()
        linkedin.linkJobApply()
        linkedin.saveJobIDS()

        break
    except Exception as e:
        prRed("Error in main: " + str(e))
        # close firefox driver
        end = time.time()
        prYellow("---Took: " + str(round((time.time() - start) / 60)) +
                 " minute(s).")
        Linkedin().driver.quit()
