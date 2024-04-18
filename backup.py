import base64
from datetime import datetime
from bs4 import BeautifulSoup
import dateutil.parser as parser
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from concurrent.futures import ThreadPoolExecutor

def createCredentials(scopes) :
    credentials = Credentials.from_authorized_user_file("token.json", scopes)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())
    return credentials

def getUnreadMessageIdAndThreadList(credentials) :
    user_id = "me"   
    INBOX = "INBOX"
    UNREAD = "UNREAD"

    gmail_service =  build("gmail", "v1", credentials = credentials)
    unread_messages = gmail_service.users().messages().list(userId = user_id ,labelIds=[INBOX, UNREAD] , maxResults = 10 ).execute()
    messages = unread_messages["messages"]
    return (gmail_service , messages) 

def getUnreadMessage(gmail_service , message) :
    user_id = "me"
    message_dictionary = {}
    message_id = message["id"]
    message_dictionary["message_id"] = message["id"]
    message = gmail_service.users().messages().get(userId = user_id , id=message_id).execute()
    print("reqeust sent")
    payload = message["payload"]
    header = payload["headers"]
    
    for data in header:
        if data["name"] == "Subject":
            msg_subject = data["value"]
            message_dictionary["Subject"] = msg_subject
        if data["name"] == "Date":
            msg_date = data["value"]
            date_parse = parser.parse(msg_date)
            date = date_parse.date()
            message_dictionary["Date"] = str(date)
        if data["name"] == "To" :
            msg_to = data["value"]
            message_dictionary["msg_to"] = msg_to
        if data["name"] == "From":
            msg_from = data["value"]
            message_dictionary["Sender"] = msg_from
    message_dictionary["message_snippet"] = message["snippet"]

    try : 
        parts = payload["parts"]
        first_part = parts[0]
        first_part_body = first_part["body"]
        first_part_data = first_part_body["data"]
        cleaned_first_part = first_part_data.replace("-" , "+").replace("_" , "/")
        base_64_converted = base64.b64decode(bytes(cleaned_first_part , "UTF-8"))
        soup = BeautifulSoup(base_64_converted , "lxml")
        message_body = soup.body()
        message_dictionary["message_body"] = message_body
    except Exception as e : 
        pass
    
    return message_dictionary

def retrieveUnreadMessageList(gmail_service , message_list) :
    with ThreadPoolExecutor() as executor : 
        unread_messages_data = [executor.submit(getUnreadMessage , gmail_service , message) for message in message_list ]
        print(unread_messages_data)
    return list(unread_messages_data)

def createNewList(gmail_service , unread_message_list) :
    l = []
    for message in unread_message_list :
        l.append((gmail_service , message))
    return l

if __name__ == "__main__" : 
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
    credentials = createCredentials(SCOPES)
    gmail_service , unread_message_list = getUnreadMessageIdAndThreadList(credentials)
    unread_message_data = retrieveUnreadMessageList(gmail_service , unread_message_list)
    print(unread_message_data)