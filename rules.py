rules = {
        "From" : { 
            "predicate" : "contains",
            "value" : "piyush", 
        } , 
        "Subject" : { 
            "predicate" : "contains" , 
            "value" : "meet" , 
        } ,
        "Date" : {
            "predicate" : "is less than" ,  
            "value" : 0 , 
        }

}

tasks = {
    "all" : ["move_to_inbox" , "mark_read"] ,
    "any" : ["mark_read"]
}