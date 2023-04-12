import base64
from email.mime.text import MIMEText
from textwrap import wrap
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

# HIBP api key
hibpKey = "cacce55b529b4171b5f6da73c6163f75"

# google auth
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

def hibp(to):

    # grabs all breached account infor from HIBP
    url = ("https://haveibeenpwned.com/api/v3/breachedaccount/" + to + "?truncateResponse=false?includeUnverified=false")
    headers = {"hibp-api-key": hibpKey}
    response = requests.get(url, headers=headers)

    # appends data to the body of text to be sent in the email
    if response.status_code == 200:  # 200 is the code the api uses if the email has been found in the HIBP database
        breaches = response.json()
        msg = ""
        for breach in breaches:
            msg += f"Breach: {breach['Name']}\n"
            if 'BreachDate' in breach:
                msg += f"Date: {breach['BreachDate']}\n"
            if 'DataClasses' in breach:
                msg += f"Compromised Data: {breach['DataClasses']}\n"
                msg += "\n"
        modifyBody(to, msg)
    elif response.status_code == 404:   # 404 is the code the api uses if the email is not found in the HIBP db
        msg = f"The email address {to} was not found in any breaches."
        modifyBody(to, msg)
    else:
        msg = "Error: Something went wrong with the request."
    print("\n" + msg)

def modifyBody(to,msg):  # give the email body a more human interaction than just a message dump
    bTxt = "Hello user,\n\nYou took part in a survey for Cameron Garratt's study on Analysing AI and its Effect on the Field of Cybersecurity. You took part in the survey Social Engineering and AI Awareness and agreed to have your email put into https://haveibeenpwned.com/ \nYour email address was found in the following breaches:\n\n"
    mTxt = msg
    fTxt = "\n\nYou can view more details on the breaches listed above at https://haveibeenpwned.com/\n\n\nThank you for taking part in this project,\nCameron Garratt\n\n\nNOTE:\nThis is currently the test before AI has been enabled, please save this email address to see the difference in the AI generated email and this email."
    msg = bTxt + mTxt + fTxt
    wrap(msg)
    sendEmail(to,msg)

def sendEmail(to, msg):

    # send email to user email
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(msg)
    message['to'] = to
    message['subject'] = 'Spear Alert email'
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'sent message to {message} Message Id: {message["id"]}')
    except HTTPError as error: \
            print(F'An error occurred: {error}')
    message = None


def logo():  # prints the logo at the top of the program
    print("#################################################################################")
    print("#    #####                                    #                                 #")
    print("#   #     # #####  ######   ##   #####       # #   #      ###### #####  #####   #")
    print("#   #       #    # #       #  #  #    #     #   #  #      #      #    #   #     #")
    print("#    #####  #    # #####  #    # #    #    #     # #      #####  #    #   #     #")
    print("#         # #####  #      ###### #####     ####### #      #      #####    #     #")
    print("#   #     # #      #      #    # #   #     #     # #      #      #   #    #     #")
    print("#    #####  #      ###### #    # #    #    #     # ###### ###### #    #   #     #")
    print("#################################################################################")

if __name__ == "__main__":
    logo() #prints logo
    to = input("What is the test users email address: \n")
    hibp(to) #pull info from the HIBP API
