import time
import re
from datetime import datetime 

import dateparser
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

def generate_proxy():
    """
        Proxies for proxy seller

        Your proxy:
        154.16.177.250
        45.170.255.87
    """
    return {
        'proxy': {
            'http': 'http://arherrera0:FHWoD6r67f@45.170.255.87:50100',
            'https': 'https://arherrera0:FHWoD6r67f@45.170.255.87:50100',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }

def set_login(driver):
    email = driver.find_element(By.NAME, "user[email]")
    email.send_keys(EMAIL)

    password = driver.find_element(By.NAME, "user[password]")
    password.send_keys(PASSWORD)

    checkbox = driver.find_element(By.XPATH, """//label[@for="policy_confirmed"]""")
    checkbox.click()

    button = driver.find_element(By.NAME, "commit")
    button.click()

    # wait the page loads full 
    driver.implicitly_wait(10)

def get_current_appointment(driver):
    wait = WebDriverWait(driver, 10)
    continue_button = wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Continuar')))

    consular_appt = driver.find_element(By.CLASS_NAME, "consular-appt")
    asc_appt = driver.find_element(By.CLASS_NAME, "asc-appt")

    consular_appt_text = consular_appt.text
    asc_appt_text = asc_appt.text

    # pattern for extract date
    pattern = r"\d{1,2}\s\w+,\s\d{4}"

    # find dates
    match_1 = re.search(pattern, consular_appt_text)
    match_2 = re.search(pattern, asc_appt_text)

    if match_1 and match_2:
        date_str_1 = match_1.group()
        date_str_2 = match_1.group()

        date_consular = dateparser.parse(date_str_1).strftime('%Y-%m-%d')
        date_asc = dateparser.parse(date_str_2).strftime('%Y-%m-%d')

        return date_consular, date_asc

def set_single_appointment(type_appointment, input_cities, input_date_name, input_time_name) -> bool:
    """
        Function that set appointment from consulate or ASC
    """
    if type_appointment == 'consulate':
        element_validation = driver.find_element(By.ID, "consulate_date_time_not_available")
        cities_names = ["Guadalajara", "Mexico City", "Monterrey"]

    elif type_appointment == 'asc':
        element_validation = driver.find_element(By.ID, "asc_date_time_not_available")
        cities_names = ["Guadalajara ASC", "Mexico City ASC", "Monterrey ASC"]

    # wait for 10 seconds for inputs 
    wait = WebDriverWait(driver, 10)

    for city in cities_names:
        # select current city
        input_cities.select_by_visible_text(city)
        time.sleep(2)
        print(f"Appointment {type_appointment}")
        print(f"City: {city}")

        # check if there are appointments
        if element_validation.is_displayed():
            print(f"There aren't appointments on {city}")
            continue
        
        # get inputs and validation from inputs
        try:
            input_date = wait.until(EC.presence_of_element_located((By.ID, input_date_name)))
            input_time = wait.until(EC.presence_of_element_located((By.ID, input_time_name)))
        except Exception as e:
            print(f"There aren't appointments on {city}")
            print(e)
            continue

        # click consular dates
        input_date.click()

        # get div from datepicker
        datepicker = driver.find_element(By.ID, 'ui-datepicker-div')

        # try on consulate 
        while True:
            month = driver.find_element(By.CLASS_NAME, 'ui-datepicker-month').text
            year = driver.find_element(By.CLASS_NAME, 'ui-datepicker-year').text
            if year == "2025": break

            # finds all td for dates
            tds = datepicker.find_elements(By.TAG_NAME, 'td')

            # iterate over all dates opn next two months
            available_dates = []
            for td in tds:
                if "ui-state-disabled" not in td.get_attribute("class"):
                    available_dates.append(td)

            # iterate over available dates
            for td in available_dates:
                month = int(td.get_attribute('data-month'))
                year = int(td.get_attribute('data-year'))
                day = int(td.find_element(By.TAG_NAME, 'a').text)
                date = datetime(year=year, month=month+1, day=day).strftime('%Y-%m-%d')
                print("Display date", td.get_attribute("outerHTML"), date)
                # select this date
                td.click()
                print("Waiting Hours")
                time.sleep(15)
                # check hours
                options = input_time.find_elements(By.XPATH, './/option[@value]')
                print(f"Hours", input_time.get_attribute('outerHTML'))
                if not options: continue
                hour = options[0].get_attribute("value")
                options[0].click()
                print("Display Hour", hour)
                return True

            # get next months
            next_button = driver.find_element(By.CLASS_NAME, 'ui-datepicker-next')
            next_button.click()

            # wait for refresh date picker
            driver.implicitly_wait(2)
            
    return False

def set_appointment() -> bool:
    """
        Try to advance appointment 

        this function search on Mexico, GDL and MTY
    """
    print("Current dates")
    print(f"Consular: {date_consular}")
    print(f"ASC: {date_asc}")
    
    # set appointment on consulate
    input_cities = Select(driver.find_element(By.ID, "appointments_consulate_appointment_facility_id"))
    input_date_name = "appointments_consulate_appointment_date_input"
    input_time_name = "appointments_consulate_appointment_time"
    status = set_single_appointment('consulate', input_cities, input_date_name, input_time_name)
    print(f"Consulate appointment {status}")
    if not status: return False

    # set appointment on asc
    input_cities = Select(driver.find_element(By.ID, "appointments_asc_appointment_facility_id"))
    input_date_name = "appointments_asc_appointment_date_input"
    input_time_name = "appointments_asc_appointment_time"
    status = set_single_appointment('asc', input_cities, input_date_name, input_time_name)
    print(f"ASC appointment {status}")
    if not status: return False

    return True


if __name__ == '__main__':
    EMAIL = "olgaclz@hotmail.com"
    PASSWORD = "visa_test_2020"

    # create driver
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('--incognito')
    # options.add_argument('--headless')
    options_proxy = generate_proxy()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options, seleniumwire_options=options_proxy)
    # driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://ais.usvisa-info.com/es-mx/niv/users/sign_in")
        set_login(driver)
        date_consular, date_asc = get_current_appointment(driver)
        driver.get("https://ais.usvisa-info.com/es-mx/niv/schedule/46717687/appointment")
        
        # try to set new appointment
        status = set_appointment()

    except Exception as e:
        print(e)
    finally:
        pass
        # driver.quit()

