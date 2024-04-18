from fields import message_fields
from kmp import KMP
from rules import rules
from datetime import datetime , timedelta , date
import pymysql
import os

def processDate(given_date , days) :
    given_date = datetime.strptime(given_date, "%Y-%m-%d")
    todays_date = datetime.now()
    prev_date = todays_date-timedelta(days=days)
    return given_date <= prev_date

def processMessage(message) :
    kmp = KMP()
    from_field_data = message[message_fields["From"]].lower()
    from_field_rule = rules[message_fields["From"]]
    predicate = from_field_rule["predicate"]
    check_string = from_field_rule["value"]
    from_field = False
    if predicate == "contains" : 
        from_field = kmp.checkStringExists(from_field_data , check_string)
    elif predicate == "does not contains" :
        from_field = not kmp.checkStringExists(from_field_data , check_string)
    
    subject_field_data = message[message_fields["Subject"]].lower()
    subject_field_rule = rules[message_fields["Subject"]]
    predicate = subject_field_rule["predicate"]
    subject_field = False
    check_string = subject_field_rule["value"]
    if predicate == "contains" :
        subject_field = kmp.checkStringExists(subject_field_data , check_string)
    elif predicate == "does not contains" :
        subject_field = not kmp.checkStringExists(subject_field_data , check_string)
    
    date_field_data = message[message_fields["Date"]]
    date_field_rule = rules[message_fields["Date"]]
    predicate = date_field_rule["predicate"]
    check_value = date_field_rule["value"]
    date_field = False
    if predicate == "is less than" : 
        date_field = processDate(date_field_data , check_value)
    
    all_values = from_field and date_field and subject_field
    any_values = from_field or date_field or subject_field
    return_value = ["none" , message["message_id"]]
    if any_values : 
        return_value[0] = "any"
    if all_values : 
        return_value[0] = "all"
    print(f"From field : {from_field}")
    print(f"Subject field : {subject_field}")
    print(f"Date Field : {date_field}")
    print("="*60)
    return return_value
        

def processMessageList(message_list) :
    connection = pymysql.connect(
        host = "localhost" , 
        user = "root" , 
        password = os.environ.get("MYSQL_PASSWORD") , 
        database = "happyfox_project" , 
    )
    cursor = connection.cursor()
    connection.commit()
    processed_list = []
    for message in message_list :
        print(message["message_id"][:20] )
        print(message["Subject"][:100] )
        print(message["Date"][:20] )
        print(message["msg_to"][:30] )
        print(message["From"][:200] )
        print(message["message_body"][:100] )
        print(message["message_snippet"][:100])
        
        
        
        
        
        
        query = """INSERT INTO email_data (message_id , Subject , Date , msg_to , msg_from , message_body , message_snippet ) VALUES (%s , %s ,%s ,%s , %s ,%s , %s ) """ 
        try : 
            cursor.execute(
                query , 
                (
                    str(message["message_id"][:20] ),  
                    str(message["Subject"][:100] ),  
                    str(message["Date"][:20] ),  
                    str(message["msg_to"][:30] ),  
                    str(message["From"][:200] ),  
                    str(message["message_body"][:100] ),  
                    str(message["message_snippet"][:100])
                )
            )
            connection.commit()
        except Exception as e: 
            print(e)
        processed_list.append(processMessage(message))
    return processed_list   
    
processMessageList([])