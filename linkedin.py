import time
import math
import random
import os
import utils
import finders
import constants
import config_local
import platform

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from utils import prRed, prYellow, prGreen

from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import os

from concurrent.futures import ThreadPoolExecutor

class Linkedin:

    def __init__(self):
        browser = config_local.browser[0].lower()
        linkedinEmail = config_local.email
        if browser == "firefox":
            if len(linkedinEmail) > 0:
                print(platform.system())
                if platform.system == "Linux":
                    prYellow(
                        "On Linux you need to define profile path to run the bot with Firefox. Go about:profiles find root directory of your profile paste in line 8 of config file next to firefoxProfileRootDir "
                    )
                    exit()
                else:
                    os.system("taskkill /im geckodriver.exe /f")
                    os.system("taskkill /im firefox.exe /f")
                    self.driver = webdriver.Firefox()
                    self.driver.get(
                        "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin"
                    )
                    prYellow("Trying to log in linkedin.")
                    try:
                        utils.wait_until_visible_and_find(self.driver,
                            "id", "username").send_keys(linkedinEmail)
                        utils.wait_until_visible_and_find(self.driver,"id", "password").send_keys(
                            config_local.password)

                        utils.wait_until_visible_and_find(self.driver,
                            "xpath",
                            '//*[@id="organic-div"]/form/div[3]/button').click(
                            )
                    except Exception as e:
                        prRed(e)
            else:
                os.system("taskkill /im geckodriver.exe /f")
                os.system("taskkill /im firefox.exe /f")
                self.driver = webdriver.Firefox(options=utils.browserOptions())
        elif browser == "chrome":
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
            self.driver.get(
                "https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin"
            )
            prYellow("Trying to log in linkedin.")
            try:
                utils.wait_until_visible_and_find(self.driver,"id",
                                         "username").send_keys(linkedinEmail)
                time.sleep(5)
                utils.wait_until_visible_and_find(self.driver,"id", "password").send_keys(
                    config_local.password)
                time.sleep(5)
                utils.wait_until_visible_and_find(self.driver,
                    "xpath",
                    '//*[@id="organic-div"]/form/div[3]/button').click()
            except:
                prRed(
                    "Couldnt log in Linkedin by using chrome please try again for Firefox by creating a firefox profile."
                )

        # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        # webdriver.Chrome(ChromeDriverManager().install())
        # webdriver.Firefox(options=utils.browserOptions())

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
        offerPage = "https://www.linkedin.com/jobs/view/" + \
            str(jobID)

        self.driver.get(offerPage)
        time.sleep(random.uniform(1, constants.botSpeed))

        countJobs += 1

        jobProperties = self.getJobProperties(countJobs)
        button = self.easyApplyButton()
        for blacklistword in config_local.blacklist:
            if blacklistword in jobProperties:
                print(
                    "Blacklisted word found in url - skipping (" +
                    blacklistword + ")")
                button = False
            time.sleep(random.uniform(1, constants.botSpeed))

        if button is not False:
            button.click()
            WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div/div[contains(@class, 'jobs-easy-apply-modal')]"))).click()
            countApplied += 1
            try:
                utils.wait_until_visible_and_find(self.driver,
                    By.CSS_SELECTOR,
                    "button[aria-label='Submit application']",
                ).click()

                lineToWrite = (jobProperties + " | " +
                                "* 🟢 Just Applied to this job: " +
                                str(offerPage))
                self.displayWriteResults(lineToWrite)

            except:
                try:
                    utils.wait_until_visible_and_find(self.driver,
                        By.CSS_SELECTOR,
                        "button[aria-label='Continue to next step']",
                    ).click()

                    comPercentage = self.driver.find_element(
                        By.XPATH,
                        "html/body/div[3]/div/div/div[2]/div/div/span",
                    ).text
                    percenNumber = int(
                        comPercentage[0:comPercentage.index("%")])
                    result = self.applyProcess(
                        percenNumber, offerPage)
                    lineToWrite = jobProperties + " | " + result
                    self.displayWriteResults(lineToWrite)

                except Exception as e:
                    try:
                        try:
                            self.driver.find_element(
                                By.CSS_SELECTOR,
                                "option[value='urn:li:country:" +
                                config_local.country_code + "']",
                            ).click()
                            time.sleep(
                                random.uniform(
                                    1, constants.botSpeed))
                        except:
                            a = None
                        try:
                            self.driver.find_element(
                                By.CSS_SELECTOR,
                                "input").send_keys(
                                    config_local.phone_number)
                            time.sleep(
                                random.uniform(
                                    1, constants.botSpeed))
                        except:
                            a = None
                        try:
                            utils.wait_until_visible_and_find(self.driver,
                                By.CSS_SELECTOR,
                                "button[aria-label='Continue to next step']",
                            ).click()
                            time.sleep(
                                random.uniform(
                                    1, constants.botSpeed))
                        except:
                            a = None
                        comPercentage = self.driver.find_element(
                            By.XPATH,
                            "html/body/div[3]/div/div/div[2]/div/div/span",
                        ).text
                        percenNumber = int(
                            comPercentage[0:comPercentage.index("%"
                                                                )])
                        result = self.applyProcess(
                            percenNumber, offerPage)
                        lineToWrite = jobProperties + " | " + result
                        self.displayWriteResults(lineToWrite)
                    except Exception as e2:
                        print(e2)
                        lineToWrite = (
                            jobProperties + " | " +
                            "* 🔴 Cannot apply to this Job! " +
                            str(offerPage))
                        self.displayWriteResults(lineToWrite)
                        quit()
        else:
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
                    countApplied, countJobs = self.go_through_offers(jobID, countApplied, countJobs)
                # with ThreadPoolExecutor() as executor:
                #     futures = [executor.submit(self.go_through_offers, self, jobID, countApplied, countJobs) for jobID in offerIds]
                #     for futures in futures:
                #         countApplied2, countJobs2 = futures.result()
                #         countApplied += countApplied2
                #         countJobs += countJobs2

                #     # need to get a better page
                #     offerPage = "https://www.linkedin.com/jobs/view/" + \
                #         str(jobID)

                #     self.driver.get(offerPage)
                #     time.sleep(random.uniform(1, constants.botSpeed))

                #     countJobs += 1

                #     jobProperties = self.getJobProperties(countJobs)
                #     button = self.easyApplyButton()
                #     for blacklistword in config_local.blacklist:
                #         if blacklistword in jobProperties:
                #             print(
                #                 "Blacklisted word found in url - skipping (" +
                #                 blacklistword + ")")
                #             button = False
                #         time.sleep(random.uniform(1, constants.botSpeed))

                #     if button is not False:
                #         button.click()
                #         WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.XPATH, "//div/div[contains(@class, 'jobs-easy-apply-modal')]"))).click()
                #         countApplied += 1
                #         try:
                #             utils.wait_until_visible_and_find(self.driver,
                #                 By.CSS_SELECTOR,
                #                 "button[aria-label='Submit application']",
                #             ).click()

                #             lineToWrite = (jobProperties + " | " +
                #                            "* 🟢 Just Applied to this job: " +
                #                            str(offerPage))
                #             self.displayWriteResults(lineToWrite)

                #         except:
                #             try:
                #                 utils.wait_until_visible_and_find(self.driver,
                #                     By.CSS_SELECTOR,
                #                     "button[aria-label='Continue to next step']",
                #                 ).click()
                #                 time.sleep(
                #                     random.uniform(1, constants.botSpeed))
                #                 comPercentage = utils.wait_until_visible_and_find(self.driver,
                #                     By.XPATH,
                #                     "html/body/div[3]/div/div/div[2]/div/div/span",
                #                 ).text
                #                 percenNumber = int(
                #                     comPercentage[0:comPercentage.index("%")])
                #                 result = self.applyProcess(
                #                     percenNumber, offerPage)
                #                 lineToWrite = jobProperties + " | " + result
                #                 self.displayWriteResults(lineToWrite)

                #             except Exception as e:
                #                 try:
                #                     try:
                #                         utils.wait_until_visible_and_find(self.driver,
                #                             By.CSS_SELECTOR,
                #                             "option[value='urn:li:country:" +
                #                             config_local.country_code + "']",
                #                         ).click()
                #                         time.sleep(
                #                             random.uniform(
                #                                 1, constants.botSpeed))
                #                     except:
                #                         a = None
                #                     try:
                #                         utils.wait_until_visible_and_find(self.driver,
                #                             By.CSS_SELECTOR,
                #                             "input").send_keys(
                #                                 config_local.phone_number)
                #                         time.sleep(
                #                             random.uniform(
                #                                 1, constants.botSpeed))
                #                     except:
                #                         a = None
                #                     try:
                #                         utils.wait_until_visible_and_find(self.driver,
                #                             By.CSS_SELECTOR,
                #                             "button[aria-label='Continue to next step']",
                #                         ).click()
                #                         time.sleep(
                #                             random.uniform(
                #                                 1, constants.botSpeed))
                #                     except:
                #                         a = None
                #                     comPercentage = utils.wait_until_visible_and_find(self.driver,
                #                         By.XPATH,
                #                         "html/body/div[3]/div/div/div[2]/div/div/span",
                #                     ).text
                #                     percenNumber = int(
                #                         comPercentage[0:comPercentage.index("%"
                #                                                             )])
                #                     result = self.applyProcess(
                #                         percenNumber, offerPage)
                #                     lineToWrite = jobProperties + " | " + result
                #                     self.displayWriteResults(lineToWrite)
                #                 except Exception as e2:
                #                     print(e2)
                #                     lineToWrite = (
                #                         jobProperties + " | " +
                #                         "* 🔴 Cannot apply to this Job! " +
                #                         str(offerPage))
                #                     self.displayWriteResults(lineToWrite)
                #                     quit()
                #     else:
                #         lineToWrite = (jobProperties + " | " +
                #                        "* 🟡 Already applied or Error to acquire button! Job: " +
                #                        str(offerPage))
                #         self.displayWriteResults(lineToWrite)

            prYellow("Category: " + urlWords[0] + "," + urlWords[1] +
                     " applied: " + str(countApplied) + " jobs out of " +
                     str(countJobs) + ".")

        utils.donate(self)

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
            prYellow("Warning in getting jobTitle: " + str(e)[0:50])
            jobTitle = ""
        try:
            jobCompany = self.driver.find_element(
                By.XPATH,
                "//a[contains(@class, 'ember-view') and contains(@class, 't-black')]",
            ).get_attribute("innerText").strip()
        except Exception as e:
            prYellow("Warning in getting jobCompany: " + str(e)[0:50])
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
            prYellow("Warning in getting jobApplications: " + str(e)[0:50])
            jobApplications = ""

        textToWrite = (str(count) + " | " + jobTitle + " | " + jobCompany +
                       " | " + jobApplications)
        return textToWrite

    def easyApplyButton(self):
        try:
            button = self.driver.find_element(
                By.XPATH,
                '//div[contains(@class, "jobs-apply-button--top-card")]/button[contains(@class, "jobs-apply-button")]',
            )
            EasyApplyButton = button
        except:
            EasyApplyButton = False
        time.sleep(random.uniform(1, constants.botSpeed))

        if EasyApplyButton is not False:
            if "Easy Apply" not in button.text:
                EasyApplyButton = False
        return EasyApplyButton

    def submitFound(self):
        try:
            self.driver.find_element(
                By.CSS_SELECTOR,
                "button[aria-label='Submit application']").click()
        except:
            a = None
        try:
            utils.wait_until_visible_and_find(self.driver, By.XPATH, "//h3[contains(normalize-space(), 'Your application was sent')]").click()
            
            return True
        except:
            return False

    def applyProcess(self, percentage, offerPage):
        applyPages = math.floor(100 / percentage)
        result = ""
        progress = 0
        attempts = 0
        errorslist = []
        try:
            while self.submitFound() == False and attempts < 2:
                try:
                    barNow = utils.wait_until_visible_and_find(self.driver,
                        By.XPATH, "//progress").get_attribute("aria-valuenow")
                except Exception as e:
                    print("Error in getting BAR: " + str(e))
                if progress == barNow:
                    attempts += 1
                else:
                    attempts = 0
                    
                errorslist = []
                progress = barNow

                finders.check_all_THEN_fill_all(self, config_local, errorslist)

            if config_local.followCompanies is False:
                try:
                    self.driver.find_element(
                        By.CSS_SELECTOR,
                        "label[for='follow-company-checkbox']").click()
                except:
                    a = None

            try:
                self.driver.find_element(
                    By.CSS_SELECTOR,
                    "button[aria-label='Submit application']").click()
            except:
                self.driver.find_element(By.XPATH,
                                         "//*[text() = 'Application sent']")

            result = "* 🟢 Just Applied to this job: " + str(offerPage)
        except:
            result = (
                "* 🔴 " + str(applyPages) +
                " Pages, couldn't apply to this job! Extra info needed. Link: "
                + str(offerPage) +
                "\n--------------------------- errorList -----------------------------\n"
                + str(errorslist) +
                "\n------------------------------------------------------------------\n"
            )
        
        return result

    def displayWriteResults(self, lineToWrite: str):
        try:
            print(lineToWrite)
            utils.writeResults(lineToWrite)
        except Exception as e:
            prRed("Error in DisplayWriteResults: " + str(e))


start = time.time()
while True:
    try:
        Linkedin().linkJobApply()

        break
    except Exception as e:
        prRed("Error in main: " + str(e))
        # close firefox driver
        end = time.time()
        prYellow("---Took: " + str(round((time.time() - start) / 60)) +
                 " minute(s).")
        Linkedin().driver.quit()
