from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status, viewsets
from ussd.serializers import USSDRequestSerializer
from django.core.cache import cache
from ussd.helpers import api_caller
import logging

logger = logging.getLogger("django")

# Create your views here.

class UssdRequest(viewsets.ViewSet):
    def create(self, request):
        serializer = USSDRequestSerializer(data=request.data)

        logger.info("Request received ... ")
        logger.info(request.data)

        if request.method == 'POST':
            logger.info("Valid request ... ")
            text = request.POST.get('text', None)
            session_id = request.POST.get('sessionId', None)
            service_code = request.POST.get('serviceCode', None)
            phone_number = request.POST.get('phoneNumber', None)
            resp = ''

            proceed = False

            # Format phone number
            logger.info("Length of phone number is "+str(len(phone_number)))
            if len(phone_number) > 10:
                # Check first 3
                first_digits = phone_number[:3]
                if phone_number[:1] == "+":
                    first_digits = phone_number[:4]

                logger.info("First 3 numbers are "+first_digits)
                logger.info("New string is ")
                phone_number = phone_number.replace(first_digits, "0")
                proceed = True
                logger.info("New phone number is "+phone_number)


            logger.info("Session ID is ")
            logger.info(session_id)

            # Get session for the request. If session does not exist, create one
            session_key = f"ussd_session_{session_id}"
            session_data = cache.get(session_key, {})
            category = session_data.get('category', 'CUSTOMER')

            logger.info("Service key is ")
            logger.info(session_key)

            logger.info("Session data retrieved is ")
            logger.info(session_data)

            # Stage of USSD request
            stage = ""

            if 'stage' in session_data:
                stage = session_data['stage']

            # logger.info("Session list is ")
            # logger.info(request.session)

            # Check if phone number is for field mobilization or customer

            # Check if the phone number is new or an existing customer

            # Validate pin if existing

            # create new profile flow if new

            # List first 3 accounts

            # From the listed accounts, you can credit an account (Customer)

            # You can also check balance from the listed accounts

            # A field mobilization agent can perform a deposit using the field deposit api

            # check if number has been verified already. If not, check if number exists else continue with options
            if proceed == True:
                numberVerified = False
                logger.info("Number verified result is ")
                # logger.info(session_data['numberVerified'])
                if 'numberVerified' in session_data:
                    logger.info("Number has already been verified on this session")
                    if session_data['numberVerified'] == True:
                        numberVerified = True
                
                if numberVerified == False:
                    response = api_caller.checkNumberExists(phone_number)

                    if response.status_code == 200:
                        resp = response.json()
                        logger.info(resp['data'])
                        if resp['data']['StatusCode'] == 200 and resp['data']['Result'] == True:
                            # Number exists

                            # Check number category
                            response = api_caller.getNumberCategory(phone_number)

                            logger.info('Number verified')
                            session_data['numberVerified'] = True
                            stage = "NUMBER_PIN_VERIFICATION"

                            if response.status_code == 200:
                                resp = response.json()
                                if resp['data']['StatusCode'] == 200:
                                    category = resp['data']['Result']
                                    session_data['category'] = category

                            logger.info("Updated session data is ")
                            logger.info(session_data)
                            numberVerified = True
                    
                # Show existing menu if number exists
                if numberVerified == True:
                    logger.info("Text returned is "+text)
                    if text == "":
                        resp = """CON Welcome\n
                        Please enter your pin
                        """
                    else:
                        if "REGISTER" in stage:
                            if stage == "REGISTER":
                                stage = "REGISTER_CATEGORY"
                                logger.info("Updated session data is ")
                                logger.info(session_data)

                                resp = """CON 
                                    What category do you want to register under?\n
                                    1. Customer
                                    2. Field Agent
                                """
                            if stage == "REGISTER_CATEGORY":
                                stage = "REGISTER_FIRSTNAME"
                                logger.info("Updated session data is ")
                                logger.info(session_data)

                                sp_text = text.split('*')
                                text = sp_text[-1]

                                resp = """CON 
                                    Please enter your first name
                                """

                                if text == "1":
                                    session_data['register_type'] = "CUSTOMER"
                                elif text == "2":
                                    session_data['register_type'] = "FIELD"
                                else:
                                    stage = "REGISTER_CATEGORY"
                                    resp = """CON 
                                    Invalid Selection. Please select a category you want to register under.\n
                                    1. Customer
                                    2. Field Agent
                                    """
                                
                            elif stage == "REGISTER_FIRSTNAME":
                                stage = "REGISTER_LASTNAME"
                                logger.info("First name about to be saved ")
                                logger.info(text)

                                session_data['register_firstName'] = text

                                resp = """CON 
                                    Please enter your last name
                                """
                            elif stage == "REGISTER_LASTNAME":
                                stage = "REGISTER_GENDER"
                                logger.info("First name about to be saved ")
                                logger.info(text)

                                session_data['register_lastName'] = text

                                resp = """CON 
                                    Please select your gender\n
                                    1. Male
                                    2. Female
                                """
                            elif stage == "REGISTER_GENDER":
                                stage = "REGISTER_ALT_PHONE_NUMBER"
                                logger.info("First name about to be saved ")
                                logger.info(text)

                                resp = """CON 
                                    Please provide an alternate phone number\n
                                """

                                sp_text = text.split('*')
                                text = sp_text[-1]

                                if text == "1":    
                                    session_data['register_gender'] = "m"
                                elif text == "2":
                                    session_data['register_gender'] = "f"
                                else:
                                    stage = "REGISTER_GENDER"
                                    resp = """CON 
                                    Invalid selection. Please select your gender \n
                                    1. Male
                                    2. Female
                                """
                            elif stage == "REGISTER_ALT_PHONE_NUMBER":
                                stage = "REGISTER_REGISTER"
                                logger.info("Alt phone number is ")
                                logger.info(text)

                                type = session_data['register_type']
                                first_name = session_data['register_firstName']
                                last_name = session_data['register_lastName']
                                gender = session_data['register_gender']
                                alt_num = text

                                response = api_caller.register(first_name=first_name, last_name=last_name, gender=gender, phone_number=phone_number, alt_phone_number=alt_num, type=type)

                                if response.status_code == 200:
                                        resp = response.json()
                                        if resp['data']['StatusCode'] == 200:
                                            # Show main view as pin verification is successful
                                            stage = "MAIN_VIEW"
                                            logger.info("Updated session data is ")
                                            logger.info(session_data)

                                            resp = """END 
                                                Successful Registration
                                            """
                                        else:
                                            resp = """END Registration failed. Please try again."""
                                else:        
                                    resp = """END 
                                        Sorry. Registration failed.\nPlease try again later.\n
                                    """
                        else:
                            if category == 'CUSTOMER':
                                if stage == "NUMBER_PIN_VERIFICATION":
                                    response = api_caller.pinVefification(phone_number=phone_number, pin=text)

                                    if response.status_code == 200:
                                        resp = response.json()
                                        if resp['data']['StatusCode'] == 200:
                                            # Show main view as pin verification is successful
                                            logger.info("Phone number to get accounts is "+phone_number)
                                            response = api_caller.getCustAccounts(phone_number)

                                            if response.status_code == 200:
                                                resp = response.json()
                                                logger.info("Accounts are: ")
                                                logger.info(resp)
                                                if resp['data']['StatusCode'] == 200:
                                                    # Show main view as pin verification is successful
                                                    stage = "ACCOUNTS"
                                                    accounts = resp['data']['Result']
                                                    session_data['accounts'] = resp['data']['Result']
                                                    logger.info("Updated session data is ")
                                                    logger.info(session_data)

                                                    resp = "CON Your accounts:\n"
                                                    t = 1
                                                    for ac in accounts:
                                                        message = str(t)+". "+ac['AccountNumber']+"\n"
                                                        resp = resp+message
                                                        t = t+1
                                                else:
                                                    resp = "END "+resp['data']['StatusDesc']
                                        else:
                                            stage = "NUMBER_PIN_VERIFICATION"
                                            resp = """CON Invalid pin. Please try again. \nEnter Pin"""
                                    else:
                                        stage = "NUMBER_PIN_VERIFICATION"
                                        resp = """CON Invalid pin. Please try again. \nEnter Pin"""
                                elif stage == "ACCOUNTS":
                                    sp_text = text.split('*')
                                    text = sp_text[-1]
                                    accounts = session_data['accounts']
                                    logger.info("Accounts fetched from session are ")
                                    logger.info(accounts)
                                    logger.info("Text is now ")
                                    logger.info(text)
                                    logger.info("first account is ")
                                    logger.info(accounts[0])
                                    try:

                                        stage = "ACCOUNT_BALANCE"
                                        accounts = session_data['accounts']

                                        logger.info("selected account is "+accounts[int(text)-1]['AccountNumber'])

                                        response = api_caller.getAccountBalance(accounts[int(text)-1]['AccountNumber'])
                                        logger.info("Balance is: ")
                                        logger.info(response)
                                        if response.status_code == 200:
                                            resp = response.json()
                                            if resp['data']['StatusCode'] == 200:
                                                bal = resp['data']['Result']['AvailableBalance']
                                                loanBal = resp['data']['Result']['LoanBalance']
                                                resp = "END Your balance is "+str(bal)+" with a loan balance of "+str(loanBal)
                                            else:
                                                stage = "ACCOUNTS"
                                                resp = "CON Please try again. Your accounts:\n"
                                                t = 1
                                                for ac in accounts:
                                                    message = str(t)+". "+ac['AccountNumbr']+"\n"
                                                    resp = resp+message
                                                    t = t+1
                                    except Exception as e:
                                        logger.info("Error!!")
                                        logger.info(e)
                                        stage = "ACCOUNTS"
                                        resp = "CON Something went wrong. Please try again.\n"
                                        t = 1
                                        for ac in accounts:
                                            message = str(t)+". "+ac['AccountNumber']+"\n"
                                            resp = resp+message
                                            t = t+1
                                else:
                                    resp = "END Unknown selection stage"
                            elif category == 'MOBILIZATION':
                                if stage == "NUMBER_PIN_VERIFICATION":
                                    response = api_caller.pinVefification(phone_number=phone_number, pin=text)

                                    if response.status_code == 200:
                                        resp = response.json()
                                        if resp['data']['StatusCode'] == 200:
                                            # Show main view as pin verification is successful
                                            stage = "MAIN_VIEW"
                                            logger.info("Updated session data is ")
                                            logger.info(session_data)

                                            resp = """CON 1. Deposit"""
                                        else:
                                            stage = "NUMBER_PIN_VERIFICATION"
                                            resp = """CON Invalid pin. Please try again"""
                                    else:
                                        stage = "NUMBER_PIN_VERIFICATION"
                                        resp = """CON Invalid pin. Please try again"""
                                elif stage == "MAIN_VIEW":
                                    sp_text = text.split('*')
                                    text = sp_text[-1]
                                    logger.info("Selection is "+text)
                                    if text == "1":
                                        logger.info("About to display menu to enter account number")
                                        stage = "FIELD_DEPOSIT_ACCOUNT_NUMBER"
                                        resp = """CON Please enter account number
                                        """
                                    else:
                                        resp = """CON Invalid Selection. Please try again.\n
                                                1. Deposit
                                                """
                                elif stage == "FIELD_DEPOSIT_ACCOUNT_NUMBER":
                                    sp_text = text.split('*')
                                    text = sp_text[-1]
                                    session_data['field_deposit_account'] = text
                                    logger.info("Account number entered is "+text)
                                    stage = "FIELD_DEPOSIT_AMOUNT"
                                    resp = """CON Please enter amount
                                            """
                                elif stage == "FIELD_DEPOSIT_AMOUNT":
                                    sp_text = text.split('*')
                                    text = sp_text[-1]
                                    session_data['field_deposit_amount'] = text
                                    logger.info("Amount entered is "+text)

                                    response = api_caller.fieldDeposit(account_number=session_data['field_deposit_account'], amount=text, phone_number=phone_number)
                                    if response.status_code == 200:
                                        resp = response.json()
                                        if resp['data']['StatusCode'] == 200:
                                            # Show main view as pin verification is successful
                                            stage = "FIELD_DEPOSIT"
                                            logger.info("Updated session data is ")
                                            logger.info(session_data)

                                            resp = """END Deposit successful"""
                                        else:
                                            stage = "MAIN_VIEW"
                                            resp = """CON Deposit failed. Please try again.\n
                                            1. Deposit
                                            """
                                else:
                                    resp = "END Unknown selection stage"
                            else:
                                resp = "END Invalid user"
                else:
                    stage = "REGISTER"
                    session_data['numberVerified'] = True
                    resp = """CON Welcome\n
                    You are not registered. Please register.\n
                    1. Register
                    """
            else:
                resp = """END Welcome\n
                    Invalid request.
                    """
            
            logger.info("Session data about to be saved it is ")
            
            session_data['stage'] = stage
            logger.info(session_data)
            cache.set(session_key, session_data, timeout=600)
            logger.info("Sending response back")
            

            # logger.info("Session ID used to retrieve session ")
            # logger.info(session_id)
            # session_data2 = request.session.get(session_id, {})

            # logger.info("Session data 2 retrieved is ")
            # logger.info(session_data2)
            
            return HttpResponse(resp, content_type='text/plain')
        else:
            logger.info("Invalid request ...")
