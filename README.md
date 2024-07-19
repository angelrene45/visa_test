# Visa Selenium
Script to advance visa appointment

Usage:
```bash
python visa_selenium.py --email <email> --password <password> --maxyear <max-allowed-year> --mindate <min-date> --cities <cities-allowed> 
```

Example usage:
```bash
python visa_selenium.py --email <email> --password <password> --maxyear 2024 --mindate 2023-03-31 --cities GDL CDMX TJ
```


**Generate SSL Cert for selenium wire**
Since you are using selenium wire You need to install the certificate in your local machine You can also get the certificate by running the following command
```bash
python -m seleniumwire extractcert
```

**Import cert in Windows**
Move the new certificate from the Certificates-Current User > Trusted Root Certification Authorities into Certificates (Local Computer) > Trusted Root Certification Authorities.


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