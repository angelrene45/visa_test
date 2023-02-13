import requests
import json
import random
from dateutil.parser import parse

import bs4 

def generate_header():
    """
        Esta funcion nos va a generar un header dinamico a partir de 1 json y 1 txt
    """
    with open('user-agents.txt') as f: ##Listado de user agents
        list_user_agents = f.read().splitlines()
    user_agent = random.choice(list_user_agents)
    with open('json_headers.json') as json_file: #json de headers que se pueden utilizar
        headers_globals = json.load(json_file)
    header = headers_globals[str(random.randint(0, 3))]
    header["User-Agent"] = user_agent.replace('\n', '')
    return header

def generate_proxy():
    """
        Esta funcion nos va a retornar un proxy
    """
    return {
        "http": "http://arherrera0:FHWoD6r67f@45.170.255.166:50100/",
        "https": "http://arherrera0:FHWoD6r67f@45.170.255.166:50100/",
    }
   
def get_headers_with_crf_token_login(session: requests.Session, api: str):
    # Get CSRF token 
    response = session.request("GET", api)
    if response.status_code != 200: raise Exception(f"Error in api: {api}")
    html = bs4.BeautifulSoup(response.content, "html.parser")
    csrf_token = html.find('meta', attrs={'name': 'csrf-token'})['content']
    # create headers
    headers = {
        "Accept": "*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://ais.usvisa-info.com",
        "Referer": api,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "X-CSRF-Token": csrf_token
    }
    # Update headers
    headers.update(session.headers)
    headers['Cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
    return headers

def set_login(session: requests.Session):
    payload = {
        "utf8": "✓",
        "user[email]": "olgaclz@hotmail.com",
        "user[password]": "visa_test_2020",
        "policy_confirmed": 1,
        "commit": "Iniciar+sesión",
    }
    # Get Headers with CSRF token 
    headers = get_headers_with_crf_token_login(session, LOGIN_URL)

    # Authenticate User
    response = session.request("POST", LOGIN_URL, data=payload, headers=headers)
    if response.status_code != 200: raise Exception("Error in Login")

def get_headers_with_crf_token_appointment(session: requests.Session, api: str):
    pass

def set_appointment(session: requests.Session):

    url = "https://ejemplo.com/es-mx/niv/schedule/46717687/appointment"

    payload = {
        "utf8": "✓",
        "authenticity_token": "",
        "confirmed_limit_message": "1",
        "appointments[consulate_appointment][facility_id]": "65",
        "appointments[consulate_appointment][date]": "",
        "appointments[consulate_appointment][time]": "",

        "appointments[asc_appointment][facility_id]": "",
        "appointments[asc_appointment][date]": "",
        "appointments[asc_appointment][time]": "",
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = session.post(url, data=payload, headers=headers)

    print(response.text)

# API'S
LOGIN_URL = "https://ais.usvisa-info.com/es-mx/niv/users/sign_in"
APPOINTMENT_URL = "https://ais.usvisa-info.com/es-mx/niv/schedule/46717687/appointment"

# create session
session = requests.Session()
# Get header and proxy
header = generate_header()
proxy = generate_proxy()
# set header and proxy
session.headers.update(header)
session.proxies = proxy

# Login
set_login(session)

# Appointment Page
consulate = {
    "66": "Guadalajara",
    "70": "Mexico City",
    "71": "Monterrey",
}
asc = {
    "77" : "Guadalajara",
    "82" : "Mexico City",
    "83" : "Monterrey"
}
response = session.request("GET", APPOINTMENT_URL)
if response.status_code != 200: raise Exception("Error in get appointment page")
html = bs4.BeautifulSoup(response.content, "html.parser")

# get authenticity_token from <form>
input_element = html.find("input", attrs={"name": "authenticity_token"})
if not input_element: raise Exception(f'No authenticity_token: {html}')
authenticity_token = input_element["value"]
print(authenticity_token)

# get csrf_token (we need to next api calls) 
csrf_token = html.find('meta', attrs={'name': 'csrf-token'})['content']

# create headers
headers = {
    "Accept": " application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7",
    "Connection": "keep-alive",
    "Referer": APPOINTMENT_URL,
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "X-Requested-With": "XMLHttpRequest",
    "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "X-CSRF-Token": csrf_token
}
# Update headers
headers.update(session.headers)
headers['Cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
# params
params = {
    "appointments\[expedite\]": "false" 
}

# Check Consulate in GUADALAJARA
DATES_CONSULATE_URL = f"{APPOINTMENT_URL}/days/66.json"
response = session.request("GET", DATES_CONSULATE_URL, params=params, headers=headers)
dates_json = response.json()
# dates = [item['date'] for item in dates_json if '2023' in item['date']]
dates = [item['date'] for item in dates_json if '2024' in item['date'] and '-02' in item['date']]

if not dates: raise Exception(f"No 2023 Dates in Json: {dates_json}")

# iterate over each date 
for consulate_date in dates:
    # Get hours
    params = {
        "appointments\[expedite\]": "false",
        "date": consulate_date,
    }
    HOURS_CONSULATE_URL = f"{APPOINTMENT_URL}/times/66.json"
    response = session.request("GET", HOURS_CONSULATE_URL, params=params, headers=headers)
    hours_json = response.json()
    consulate_hour = hours_json['available_times'][0]

    # check in CAS Guadalajara
    params = {
        "consulate_id": "66",
        "consulate_date": consulate_date,
        "consulate_time": consulate_hour,
        "appointments\[expedite\]": "false",
    }
    DATES_CAS_URL = f"{APPOINTMENT_URL}/days/77.json"
    response = session.request("GET", DATES_CAS_URL, params=params, headers=headers)
    dates_json = response.json()
    dates_cas = [item['date'] for item in dates_json]
    if not dates_cas: continue
    # get the last date (is near to consulate appointment)
    cas_date = dates_cas[-1]

    # get hours cas
    params = {
        "date": cas_date,
        "consulate_id": "66",
        "consulate_date": consulate_date,
        "consulate_time": consulate_hour,
        "appointments\[expedite\]": "false",
    }
    HOURS_CAS_URL = f"{APPOINTMENT_URL}/times/77.json"
    response = session.request("GET", HOURS_CAS_URL, params=params, headers=headers)
    hours_json_cas = response.json()
    if not hours_json_cas: continue
    cas_hour = hours_json_cas['available_times'][0]
    
    print(f"Date Consulate: {consulate_date} => {consulate_hour}")
    print(f"Date CAS: {cas_date} => {cas_hour}")
    print("*"*20)

    # set appointment 
    url = "https://ejemplo.com/es-mx/niv/schedule/46717687/appointment"

    payload = {
        "utf8": "✓",
        "authenticity_token": authenticity_token,
        "confirmed_limit_message": "1",
        "appointments[consulate_appointment][facility_id]": "66",
        "appointments[consulate_appointment][date]": consulate_date,
        "appointments[consulate_appointment][time]": consulate_date,
        "appointments[asc_appointment][facility_id]": "77",
        "appointments[asc_appointment][date]": cas_date,
        "appointments[asc_appointment][time]": cas_hour,
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Language": "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7",
        "Connection": "keep-alive",
        "Referer": url,
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "X-Requested-With": "XMLHttpRequest",
        "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "X-CSRF-Token": csrf_token
    }

    # Update headers
    headers.update(session.headers)
    headers['Cookie'] = '; '.join([x.name + '=' + x.value for x in response.cookies])
    response = session.request("POST", url, data=payload, headers=headers)
    print(response.status_code)
    print(response.text)
    break





    
    
# https://stackoverflow.com/questions/51351443/get-csrf-token-using-python-requests
