For running the setup and file . 

You need to create an environment . 

If you are in windows , use : 

```
python -m venv happy_fox_env
```

Then activate it . 

```
.\happy_for_env\Scripts\activate
```

The install all dependencies . 

```
pip install -r requirements.txt 
```
After this , you have to run the script.py file .

The script file , firstly creates credentials to  get the gmail api . 

After that , it fetches all the data related to the mail , and then the list of mails is sent to process and at that time we check few things that the rules are met or not . 

If the rules are met , then based on the rule task is done . 

Also there is a database connection , so the data is also saved to db. 

Video link below :
[![Watch the video](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSTaAU5GAas_VoV8YCHdVG3l4i9fiFamDRMiafr6beQaA&s)](https://drive.google.com/file/d/15OA3ygaHtmQZsBvCR1xeGWxUCHo6thUk/view?usp=sharing)
Video link : https://drive.google.com/file/d/15OA3ygaHtmQZsBvCR1xeGWxUCHo6thUk/view?usp=sharing