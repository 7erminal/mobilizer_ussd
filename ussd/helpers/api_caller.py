import requests
from django.conf import settings
import logging

logger = logging.getLogger("django")

def checkNumberExists(phone_number):
    url = settings.API_URL+'/api/existing-number/'+phone_number
    logger.info("Url sent is "+url)

    # Check if the phone number is new or an existing customer
    response = requests.get(url)

    logger.info("Response received is ")
    logger.info(response.json())
    return response

def pinVefification(phone_number, pin):
    url = settings.API_URL+'/api/verify-pin/'
    logger.info("Url sent is "+url)

    params = {
            'number': phone_number,
            'password': pin
        }

    # verify pin
    response = requests.post(url, data=params)

    logger.info("Response received is ")
    logger.info(response.json())
    return response

def getNumberCategory(phone_number):
    url = settings.API_URL+'/api/number-category-validation/'+phone_number
    logger.info("Url sent is "+url)

    # verify pin
    response = requests.get(url)

    logger.info("Response received is ")
    logger.info(response.json())
    return response

def getFieldAccounts(id_):
    url = settings.API_URL+'/api/list-accounts/'
    logger.info("Url sent is "+url)

    params = {
            'id': id_,
        }

    # verify pin
    response = requests.post(url, data=params)

    logger.info("Response received is ")
    logger.info(response.json())
    return response

def getCustAccounts(phone_number):
    url = settings.API_URL+'/api/list-cust-accounts/'
    logger.info("Url sent is "+url)

    params = {
            'number': phone_number,
        }

    # verify pin
    response = requests.post(url, data=params)

    logger.info("Response received is ")
    logger.info(response.json())
    return response

def getAccountBalance(account_number):
    url = settings.API_URL+'/api/account-balance/'
    logger.info("Url sent is "+url)

    params = {
            'accountNumber': account_number,
        }

    # get account balance
    response = requests.post(url, data=params)

    logger.info("Response received is ")
    logger.info(response.json())
    return response

def fieldDeposit(account_number, amount, phone_number):
    url = settings.API_URL+'/api/field-deposit/'
    logger.info("Url sent is "+url)

    params = {
            'accountNumber': account_number,
            'amount': amount,
            'mobileNumber': phone_number
        }

    # get account balance
    response = requests.post(url, data=params)

    logger.info("Response received is ")
    logger.info(response.json())
    return response

def register(first_name, last_name, gender, phone_number, alt_phone_number, type):
    url = settings.API_URL+'/api/register-account/'
    logger.info("Url sent is "+url)

    params = {
            'firstName': first_name,
            'lastName': last_name,
            'gender': gender,
            'mobileNumber': phone_number,
            'altMobileNumber': alt_phone_number,
            'type': type
        }

    # get account balance
    response = requests.post(url, data=params)

    logger.info("Response received is ")
    logger.info(response.json())
    return response