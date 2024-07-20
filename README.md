# Visa Selenium
Script to advance visa appointment

## Linux Setup

### Setup Project
- Install Google Chrome Driver, Follow Instructions [here](https://www.wikihow.com/Install-Google-Chrome-Using-Terminal-on-Linux)
```bash
python -m venv venv
source venv/bin/activate 
python -m pip install -r requirements.txt -v
```

Usage:
```bash
python visa_selenium.py --email <email> --password <password> --maxyear <max-allowed-year> --mindate <min-date> --cities <cities-allowed> 
```

Example usage:
```bash
python visa_selenium.py --email <email> --password <password> --maxyear 2024 --mindate 2023-03-31 --cities GDL CDMX TJ

```

### Schedule Tasks in Crontab
```bash
*/15 * * * * /home/angelreh/repos/visa_test/venv/bin/python /home/angelreh/repos/visa_test/visa_selenium.py --email <email> --password <password> --maxyear 2025 --mindate 2023-03-31 --cities GDL CDMX TJ >> /var/tmp/visa_`date +\%Y_\%m_\%d_\%H_\%M`.log 2>&1
```

## Windows Setup 

### Generate SSL Cert for selenium wire
Since you are using selenium wire You need to install the certificate in your local machine You can also get the certificate by running the following command
```bash
python -m seleniumwire extractcert
```

### Import cert in Windows
Move the new certificate from the Certificates-Current User > Trusted Root Certification Authorities into Certificates (Local Computer) > Trusted Root Certification Authorities.


## How to setup gmail 
You can follow this [Tutorial](https://www.youtube.com/watch?v=kTcmbZqNiGw)

## Proxies
We are using 10 proxies for $10/Month on [InstantProxies.com](InstantProxies.com)

## Cities Availables

**Cita Consulado**
- Ciudad Juarez
- Guadalajara
- Hermosillo
- Matamoros
- Merida
- Mexico City
- Monterrey
- Nogales
- Nuevo Laredo
- Tijuana


**Cita CAS**
- Ciudad Juarez ASC
- Guadalajara ASC
- Hermosillo ASC
- Matamoros ASC
- Merida ASC
- Mexico City ASC
- Monterrey ASC
- Nogales ASC
- Nuevo Laredo ASC
- Tijuana ASC