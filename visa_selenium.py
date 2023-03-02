"""
    Example usage:
    python visa_selenium.py --email ar.herrera0@gmail.com --password visaAngel1997
    python visa_selenium.py --email olgaclz@hotmail.com --password visa_test_2020
"""
import time
import re
import random
import argparse
from datetime import datetime 

import dateparser
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

def generate_proxy():
    """
        Proxies from proxy seller
    """
    proxies = [
        "166.88.125.193:8800",
        "185.206.128.134:8800",
        "185.206.128.49:8800",
        "166.88.125.75:8800",
        "196.51.149.86:8800",
        "196.51.149.63:8800",
        "185.206.128.217:8800",
        "185.206.128.97:8800",
        "196.51.146.104:8800",
        "196.51.146.46:8800"
    ]
    # the first time send random proxy
    random_number = random.randint(0, len(proxies)-1)
    yield {
        'proxy': {
            'http': f'http://{proxies[random_number]}',
            'https': f'https://{proxies[random_number]}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }

    # after first try now send proxy in order
    for proxy in proxies:
        yield {
            'proxy': {
                'http': f'http://{proxy}',
                'https': f'https://{proxy}',
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
    try:
        wait = WebDriverWait(driver, 4)
        continue_button = wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Continuar')))

        # get date from consulate appointment
        consular_appt = driver.find_element(By.CLASS_NAME, "consular-appt")
        asc_appt = driver.find_element(By.CLASS_NAME, "asc-appt")

        # get date from asc appointment
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
    except Exception as e:
        print("There aren't current appointments")
        print("Use default dates")
        return '2024-08-30', '2024-08-30'

def navigate_appointment_page():
    wait = WebDriverWait(driver, 5)
    continue_button = wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'Continuar')))
    href_continue = continue_button.get_attribute("href")
    id_appointment = href_continue.split('/')[6]
    appointment_page = f"{BASE_URL}/schedule/{id_appointment}/appointment"
    # navigate to appointment page
    driver.get(appointment_page)

def exist_appointments_on_current_city(type_appointment):
    if type_appointment == 'consulate':
        element_validation = driver.find_element(By.ID, "consulate_date_time_not_available")
    elif type_appointment == 'asc':
        element_validation = driver.find_element(By.ID, "asc_date_time_not_available")

    if element_validation.is_displayed():
        print(f"There aren't appointments on {type_appointment}")
        return False
    
    return True

def set_single_appointment(type_appointment, input_cities, input_date_name, input_time_name) -> bool:
    """
        Function that set appointment from consulate or ASC
    """
    if type_appointment == 'consulate':
        cities_names = ["Guadalajara", "Mexico City", "Monterrey"]
        cities_names = ["Guadalajara"]

    elif type_appointment == 'asc':
        cities_names = ["Guadalajara ASC", "Mexico City ASC", "Monterrey ASC"]
        cities_names = ["Guadalajara ASC"]

    # wait for 10 seconds for inputs 
    wait = WebDriverWait(driver, 10)
    print(f"Appointment {type_appointment}")

    # try on every city on the list
    for city in cities_names:
        # select current city
        input_cities.select_by_visible_text(city)
        time.sleep(1)
        print(f"City: {city}")

        # check if there are appointments
        if not exist_appointments_on_current_city(type_appointment):
            print(f"There aren't appointments on {city}")
            continue # continue with next city
        
        # get inputs and validation from inputs
        try:
            input_date = wait.until(EC.presence_of_element_located((By.ID, input_date_name)))
            input_time = wait.until(EC.presence_of_element_located((By.ID, input_time_name)))
        except Exception as e:
            print(f"There aren't appointments on {city}")
            print(e)
            continue # continue with next city

        # click consular dates (open date picker)
        input_date.click()

        # try on consulate 
        date_greater_than_current = False
        while True:
            # get div from date picker
            datepicker = driver.find_element(By.ID, 'ui-datepicker-div')
            month = driver.find_element(By.CLASS_NAME, 'ui-datepicker-month').text
            year = driver.find_element(By.CLASS_NAME, 'ui-datepicker-year').text
            if year == "2025" or date_greater_than_current: break

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
                print("Display date", date)

                # check the date is lower than current_date
                current_date = datetime.strptime(date_consular, '%Y-%m-%d')
                new_date = datetime.strptime(date, '%Y-%m-%d')
                if new_date > current_date:
                    print(f"Date {new_date} is greater than current date {current_date}, skip {city} appointments")
                    date_greater_than_current = True
                    # hide date picker (click on any element for hide datepicker)
                    li_element = driver.find_element(By.CLASS_NAME, "stepPending")
                    li_element.click()
                    break # continue with next city

                # check date is greater than minimum date
                minimum_date = datetime(2023, 3, 15)
                if new_date < minimum_date:
                    print(f"Date {new_date} is lower than minimum date {minimum_date}")
                    continue # continue with next date

                # here the date is well so now select date 
                td.click()
                
                # now we wait for get the time (hours available)
                attempt = 1
                while True:
                    attempt += 1
                    # get options with hours (ignore empty hour)
                    options = input_time.find_elements(By.XPATH, './/option[@value and normalize-space(@value)!=""]')
                    if options:
                        break
                    else:
                        time.sleep(2)
                        if attempt >= 10: break

                # check hours
                if not options:
                    input_date.click() # show again the date picker
                    time.sleep(1) # wait 1 seconds 
                    continue # try with next date on date picker
                
                # select the first available hour
                hour = options[0].get_attribute("value")
                options[0].click()
                print("Display Hour", hour)
                if hour:
                    msg = f"{'*'*50}\n" \
                          f"Appointment {type_appointment} \n" \
                          f"Date: {date} \n"\
                          f"Hour: {hour} \n" \
                          f"{'*'*50}\n"
                    print(msg)
                    return True

            # get next months
            next_button = driver.find_element(By.CLASS_NAME, 'ui-datepicker-next')
            if next_button.is_displayed(): next_button.click()

            # wait for refresh date picker
            driver.implicitly_wait(2)
            
    return False

def set_appointment() -> bool:
    """
        Try to advance appointment 

        this function search on Mexico, GDL and MTY
    """
    msg = f"{'*'*50}\n" \
          f"Current Appointments:\n" \
          f"Consulate: {date_consular}\n" \
          f"ASC: {date_asc}:\n" \
          f"{'*'*50}\n"
    print(msg)

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

    status = button_make_appointment()
    if not status: return False

    return True

def button_make_appointment():
    # find the button
    btn_appointment = driver.find_element(By.ID, "appointments_submit")
    btn_appointment.click()

    # wait for modal
    wait = WebDriverWait(driver, 10)
    modal = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".reveal[style*='display: block;']")))

    # find the confirmation button and click 
    btn_confirm = modal.find_element(By.XPATH, ".//a[contains(@class, 'button') and contains(@class, 'alert')]")
    btn_confirm.click()

    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', type=str, help='Email form user')
    parser.add_argument('--password', type=str, help='Password from user')
    args = parser.parse_args()

    EMAIL = args.email
    PASSWORD = args.password

    # try to connect using proxy 
    options = webdriver.ChromeOptions() 
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument('--incognito')
    # options.add_argument('--headless')

    BASE_URL = "https://ais.usvisa-info.com/es-mx/niv"
    
    for proxy in generate_proxy():
        print(proxy)
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options, seleniumwire_options=proxy)
            driver.get(f"{BASE_URL}/users/sign_in")
            break # here the proxy is working
        except Exception as e:
            print(f"Error on proxy")
            # driver.quit()

    try:
        # login in page
        set_login(driver)
        # get current appointments from user
        date_consular, date_asc = get_current_appointment(driver)
        # navigate to appointment page 
        navigate_appointment_page()
        # try to set new appointment
        status = set_appointment()
        print(f"New Appointment with status: {status}")
    except Exception as e:
        print(e)
    finally:
        pass
        # driver.quit()
