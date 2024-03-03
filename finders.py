# so this kinda works but i need real logic in here

# try:
#     # default years of experiance
#     for elem in utils.wait_until_visible_and_find_all(self.driver,By.CSS_SELECTOR, 'input'):
#         elem.clear()
#         elem.send_keys(2)
#         time.sleep(random.uniform(1, constants.botSpeed))
# except:
#     a = None

import utils
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor

def check_all_THEN_fill_all(self, config_local, errorslist):

    # //*[@data-test-form-builder-radio-button-form-component] Example of radio button
    # //*[@data-test-text-entity-list-form-component] Example of select
    # //*[@data-test-single-line-text-form-component] Example of text input
    # //*[contains(@id, 'checkbox-form-component')] Example of checkbox

    results = utils.wait_until_visible_and_find_multiple_locators_parallel(
        self.driver, [
            {"By": By.XPATH, "locator_value": "//div/div[contains(@class, 'jobs-easy-apply-modal')]//*[contains(text(), 'City')]/../..//input"},
            {"By": By.XPATH, "locator_value": "//div/div[contains(@class, 'jobs-easy-apply-modal')]//*[contains(text(), 'salary')]/../input"},
            {"By": By.XPATH, "locator_value": '//input[contains(@id, "cover-letter")]'},
            {"By": By.XPATH, "locator_value": "//button[contains(@aria-label,'Continue to next step')]"},
            {"By": By.XPATH, "locator_value": "//button[contains(@aria-label,'Review your application')]"},
            {"By": By.XPATH, "locator_value": "//*[@data-test-form-builder-radio-button-form-component]"},
            {"By": By.XPATH, "locator_value": "//*[@data-test-text-entity-list-form-component]"},
            {"By": By.XPATH, "locator_value": "//*[@data-test-single-line-text-form-component]"},
            {"By": By.XPATH, "locator_value": "//*[contains(@id, 'checkbox-form-component')]"}
        ]
    )

    for i in range(len(results)):
        if results[i] != False:
          if i == 0:
              fillCity(self.driver, results[i], config_local, errorslist)
          elif i == 1:
              fillSalary(results[i], config_local, errorslist)
          elif i == 2:
              fillPresentationLetter(results[i], errorslist) 
          elif i == 3:
              continueNextStep(results[i], errorslist)
          elif i == 4:
              reviewApplication(results[i], errorslist)
          elif i == 5:
              fillRadioFields(self.driver, results[i], errorslist)
          elif i == 6:
              fillSelectFields(self.driver, results[i], errorslist)
          elif i == 7:
              fillTextFields(self.driver, results[i], errorslist)
          elif i == 8:
              fillCheckboxFields(self.driver, results[i], errorslist)
    
def continueNextStep(continueButtons, errorslist):
    for continueButton in continueButtons:
        try:
            continueButton.click()
        except:
            errorslist.append("Continue Button")

def reviewApplication(reviewButtons, errorslist):
    for reviewButton in reviewButtons:
        try:
            reviewButton.click()
        except:
            errorslist.append("Review Button")

def fillCity(driver, cities, config_local, errorslist):
    for city in cities:
        try:
            if city.get_attribute("value") == '':
                city.send_keys(config_local.Location)
                cityoption = utils.wait_until_visible_and_find(
                    driver, By.XPATH, "//div/div[contains(@class, 'jobs-easy-apply-modal')]//span/span[contains(normalize-space(), '"+config_local.specificCitySelectOption+"')]"
                ).click()
        except Exception as e:
          errorslist.append("City")

def fillSalary(salaries, config_local, errorslist):
    for salary in salaries:
        try:
            if salary.get_attribute("value") == '':
                salary.send_keys(config_local.Salary)
        except:
            errorslist.append("Salary")

def fillPresentationLetter(presentationLetters, errorslist):
    for presentationLetter in presentationLetters:
        try:
            elem.send_keys("./Presentation_Letter.pdf")
        except:
            errorslist.append("Presentation Letter")

def fillTextFields(driver, textFields, errorslist):
    try:
        for i in range(len(textFields)):
            input = driver.find_elements(By.XPATH, "//*[@data-test-single-line-text-form-component]//input")[i]
            if input.get_attribute("value") == "":
                errorslist.append(driver.find_elements(By.XPATH, "//*[@data-test-single-line-text-form-component]//label")[i].text)
    except Exception as e:
        print(e)
        errorslist.append("Text Field")

def fillSelectFields(driver, selectFields, errorslist):
    try:
        for i in range(len(selectFields)):
            select = driver.find_elements(By.XPATH, "//*[@data-test-text-entity-list-form-component]//select")[i]
            if (select.get_attribute("selectedIndex") == "0"):
                label = driver.find_elements(By.XPATH, "//*[@data-test-text-entity-list-form-component]//label/span[1]")[i].text
                options = [option.text for option in select.find_elements(By.TAG_NAME, "option")]
                
                errorslist.append({"Select Label": label, "Options": options})
    except Exception as e:
        print(e)
        errorslist.append("Select Field")

def fillRadioFields(driver, radioFields, errorslist):
    try:
        for i in range(len(radioFields)):
            radioField = radioFields[i]
            label = utils.find_child_element_s(driver, radioField, By.XPATH, "//span[contains(@class, 'label')]/span[1]")
            # label = driver.find_elements(By.XPATH, "//*[@data-test-form-builder-radio-button-form-component]//span[contains(@class, 'label')]")[i].text
            options = []
            dobreak = False
            optionElements = utils.find_child_element_s(driver, radioField, By.XPATH, "//div", True)
            for option in optionElements:
                options.append(utils.find_child_element_s(driver, option, By.XPATH, "//label").text)
                if utils.find_child_element_s(driver, option, By.XPATH, "//input").is_selected():
                    dobreak = True
            # for i2 in range(len(driver.find_elements(By.XPATH, "//div[contains(@class, 'jobs-easy-apply-form-section__grouping')][1]//fieldset//div"))):
            #     options.append(driver.find_element(By.XPATH, "//div[contains(@class, 'jobs-easy-apply-form-section__grouping')][1]//fieldset//div["+i2+"]//label").text)
            #     if driver.find_elements(By.XPATH, "//*[@data-test-form-builder-radio-button-form-component]//div//input")[i2].is_selected():
            #         dobreak = True
            if not dobreak:
                errorslist.append({"Radio Label": label, "Options": options})
    except Exception as e:
        print(e)
        errorslist.append("Radio Field")

def fillCheckboxFields(driver, checkboxFields, errorslist):
    try:
        for i in range(len(checkboxFields)):
            checkbox = checkboxFields[i]
            label = checkbox.find_elements(By.XPATH, "//div[contains(@class, 'label')]//span")[i].text
            options = []
            for i2 in range(len(checkbox.find_elements(By.XPATH, "//div[contains(@class, 'option')]")[i2])):
                options.append(option.find_elements(By.XPATH, "//label").text)
                if driver.find_element(By.XPATH, "//input")[i2].is_selected():
                    dobreak = True
            if not dobreak:
                errorslist.append({"Checkbox Label": label, "Option": options})
    except Exception as e:
        print(e)
        errorslist.append("Checkbox Field")

def fill_or_check_all_parallel(self, config_local, errorslist):
    functions = [
        check_and_fill_city, check_and_fill_salary,
        check_and_fill_presentation_letter, check_and_continue_next_step,
        check_and_review_application, check_text_fields, check_select_fields,
        check_radio_fields
    ]
    with ThreadPoolExecutor() as executor:
        for function in functions:
            executor.submit(function, self, config_local, errorslist)

def fill_or_check_all(self, config_local, errorslist):
    check_and_fill_city(self, config_local, errorslist)
    check_and_fill_salary(self, config_local, errorslist)
    check_and_fill_presentation_letter(self, errorslist)
    check_and_continue_next_step(self, errorslist)
    check_and_review_application(self, errorslist)
    check_text_fields(self, errorslist)
    check_select_fields(self, errorslist)
    check_radio_fields(self, errorslist)


def check_and_fill_city(self, config_local, errorslist):
    try:
        city = utils.wait_until_visible_and_find(
            self.driver, By.XPATH,
            "//div/div[contains(@class, 'jobs-easy-apply-modal')]//*[contains(text(), 'City')]/../..//input"
        )
        if city.get_attribute("value") == '':
            city.send_keys(config_local.Location)
            cityoption = utils.wait_until_visible_and_find(
                self.driver, By.XPATH,
                "//div/div[contains(@class, 'jobs-easy-apply-modal')]//span/span[contains(normalize-space(), '"+config_local.specificCitySelectOption+"')]"
            )
    except Exception as e:
        a = None


def check_and_fill_salary(self, config_local, errorslist):
    try:
        salary = utils.wait_until_visible_and_find(
            self.driver,
            By.XPATH,
            "//div/div[contains(@class, 'jobs-easy-apply-modal')]//*[contains(text(), 'salary')]/../input",
        )
        if salary.get_attribute("value") == '':
            salary.send_keys(config_local.Salary)
    except:
        a = None
    # try:
    #     # random yes no questions
    #     for elem in utils.wait_until_visible_and_find_all(self.driver,By.CSS_SELECTOR, 'select'):
    #         elem.select_by_value('Yes')
    # except:
    #     a = None


def check_and_fill_presentation_letter(self, errorslist):
    try:
        # presentation letter
        for elem in utils.wait_until_visible_and_find_all(
                self.driver, By.XPATH,
                '//input[contains(@id, "cover-letter")]'):
            elem.send_keys("./Presentation_Letter.pdf")
    except:
        a = None


def check_and_continue_next_step(self, errorslist):
    try:
        utils.wait_until_visible_and_find(
            self.driver, By.CSS_SELECTOR,
            "button[aria-label='Continue to next step']").click()
    except Exception as e:
        a = None


def check_and_review_application(self, errorslist):
    try:
        utils.wait_until_visible_and_find(
            self.driver, By.CSS_SELECTOR,
            "button[aria-label='Review your application']").click()
    except:
        a = None
    ##################################### NEW THINGS ########################################


def check_text_fields(self, errorslist):
    try:
        inputs = utils.wait_until_visible_and_find_all(
            self.driver,
            By.XPATH,
            "//div/div[contains(@class, 'jobs-easy-apply-modal')]//*[contains(@class,'text-input--input')]",
        )
        for i in range(len(inputs)):
            if inputs[i].get_attribute("value") == "":
                labels = utils.wait_until_visible_and_find_all(
                    self.driver,
                    By.XPATH,
                    "//div/div[contains(@class, 'jobs-easy-apply-modal')]//*[contains(@class,'text-input--input')]/..//label",
                )
                errorslist.append(labels[i].text)
    except Exception as e:
        print(e)
        a = None


def check_select_fields(self, errorslist):
    try:
        entity_list = utils.wait_until_visible_and_find_all(
            self.driver,
            By.XPATH,
            "//div/div[contains(@class, 'jobs-easy-apply-modal')]//label[contains(@for, 'text-entity-list')]/span[1]",
        )
        for i in range(len(entity_list)):
            select = utils.wait_until_visible_and_find_all(
                self.driver,
                By.XPATH,
                "//div/div[contains(@class, 'jobs-easy-apply-modal')]//select",
            )[i]
            if (select.get_attribute("selectedIndex") == "0"):
                errorslist.append(entity_list[i].text)
                for option in select.find_elements(By.TAG_NAME, "option"):
                    errorslist.append(option.text)
    except Exception as e:
        print(e)
        a = None


def check_radio_fields(self, errorslist):
    try:
        fieldsets = utils.wait_until_visible_and_find_all(
            self.driver,
            By.XPATH,
            "//div/div[contains(@class, 'jobs-easy-apply-modal')]//fieldset",
        )
        for i in range(len(fieldsets)):
            fieldset = fieldsets[i]
            question = fieldset.find_element(
                By.XPATH,
                "//span[contains(@class, 'label')]/span[1]",
            ).text
            names = []
            dobreak = False
            for option in option.find_elements(By.XPATH, "//div"):
                names.append(option.find_element(By.XPATH, "//label").text)
                if option.find_element(By.XPATH, "//input").is_selected():
                    dobreak = True
            if not dobreak:
                errorslist.append(question)
                for name in names:
                    errorslist.append(name)
    except Exception as e:
        print(e)
        a = None


#########################################################################################
