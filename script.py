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
from process import processMessageList
from fields import message_fields

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

def getUnreadMessageData(credentials) :
    user_id = "me"   
    INBOX = "INBOX"
    UNREAD = "UNREAD"

    gmail_service =  build("gmail", "v1", credentials = credentials)
    unread_messages = gmail_service.users().messages().list(userId = user_id ,labelIds=[INBOX, UNREAD] , maxResults = 50 ).execute()
    messages = unread_messages["messages"]
    message_data_list = []    
    for message in messages :
        message_dictionary = {field : "" for field in message_fields}
        message_id = message["id"]
        message_dictionary["message_id"] = message["id"]
        message = gmail_service.users().messages().get(userId = user_id , id=message_id).execute()
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
                message_dictionary["From"] = msg_from
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
        
        message_data_list.append(message_dictionary)
    return (gmail_service , message_data_list)

if __name__ == "__main__" : 
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly" ,
              "https://www.googleapis.com/auth/gmail.modify"]
    user_id = "me"
    credentials = createCredentials(SCOPES)
    gmail_service , unread_message_data_list = getUnreadMessageData(credentials)
    processed_list = processMessageList(unread_message_data_list)
    for data in processed_list :
        value , message_id = data
        match value :
            case "all" :
                gmail_service.users().messages().modify(userId=user_id, id=message_id,body={ "removeLabelIds": ["UNREAD"]}).execute()
                print(f"Message followed all the rules : marked read : {message_id}")
            case "any" :
                gmail_service.users().messages().modify(userId=user_id, id=message_id,body={ "addLabelIds" : ["INBOX"]}).execute()
                print(f"Message followed few rules : marked read : moved to inbox : {message_id}")
            case "none" : 
                ...
                