"""Main Module"""
import logging
import random
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request
from uk_covid19 import Cov19API
from apscheduler.schedulers.background import BackgroundScheduler
import pyttsx3
import requests

#DECLARATIONS#############################################
notifications = []
alarms = []

with open("config.json", "r") as read_file:
    data = json.load(read_file)
    WEATHER_API_KEY = data["weather_api_key"]
    NEWS_API_KEY = data["news_api_key"]
    NEWS_TOPIC = data["news_topic"]
    AREA_NAME = data["covid_news_area_name"]

all_nations = [
    "areaName="+AREA_NAME
]

cases_and_deaths = {
    "date": "date",
    "areaName": "areaName",
    "areaCode": "areaCode",
    "newCasesByPublishDate": "newCasesByPublishDate",
    "cumCasesByPublishDate": "cumCasesByPublishDate",
    "newDeathsByDeathDate": "newDeathsByDeathDate",
    "cumDeathsByDeathDate": "cumDeathsByDeathDate",
    "cumDeaths28DaysByDeathDateRate": "cumDeaths28DaysByDeathDateRate"
}

api = Cov19API(
    filters=all_nations,
    structure=cases_and_deaths
)

api.get_json(save_as="covid_data.json")
covid_data = api.get_json()["data"]
#########################################################

scheduler = BackgroundScheduler()
app = Flask(__name__)
@app.route('/')
@app.route('/index')
def main():
    """Detect changes in the url and redirect the changes to the suitable functions"""
    if request.args.get('alarm_item'):
        remove_alarm(request.args.get('alarm_item'))
    elif request.args.get('two'):
        schedule_alarm(request.args.get('two'),
                       request.args.get('alarm'),
                       request.args.get('news'),
                       request.args.get('weather'))
    elif request.args.get('notif'):
        remove_notifiction(request.args.get('notif'))
    return render_template("index.html",
                           notifications = notifications,
                           alarms = alarms,
                           title = "CA3 - Nicholas Latham",
                           image = "alarm.png")

def schedule_notification() -> str:
    """Randomly select either news or covid stats to add to the notifcation column,
    if there is already a 'news' item in the notificaitons column then it will
    update the item with a newer piece of news"""

    #NEWS
    news_title, news_content = get_news()
    notif_exists = False
    for notif in notifications:
        if notif["title"] == news_title:
            notif_exists = True
            break
    if not notif_exists:
        if len(notifications) <6:
            notifications.insert(0,{"title":news_title, "content":news_content})

    #COVID NEWS
    covid_news_title, covid_news_content = get_covid_news()
    notif_covid_exists = False
    for notif in notifications:
        if notif["title"] == "COVID-19 Statistics":
            notif_covid_exists = True
            break
    if not notif_covid_exists:
        notifications.insert(0,{"title":covid_news_title, "content":covid_news_content})

    #WEATHER
    weather_notif_exists = False
    notif_content = get_forecast("Exeter")
    for notif in notifications:
        if notif["title"] == "Weather":
            weather_notif_exists = True
            notif["content"] = notif_content
            break
    if not weather_notif_exists:
        notifications.insert(0,{"title":"Weather", "content":notif_content})
    return "Passed"

def remove_notifiction(notif_title:str) -> str:
    """When a notificaiton is closed, remove it from the notificaitons column
    and add another piece of news or covid stats depending on what was deleted"""
    #Remove the notification and replace it with a new one from the same topic
    for notif in notifications:
        if notif["title"] == notif_title:
            notifications.remove({"title":notif["title"],"content":notif["content"]})
    return "Passed"

def remove_alarm(alarm_title:str) -> str:
    """Remove the alarm fro mthe alarm column and cancel the schedules job"""
    #Remove alarms and cancel the schedules announcement
    for alarm in alarms:
        if alarm["title"] == alarm_title:
            alarms.remove({"title":alarm["title"],"content":alarm["content"]})
            if (scheduler.get_job(alarm_title)) is not None:
                scheduler.remove_job(alarm_title)
            break
    return "Passed"

def trigger_alarm(alarm_name:str, news:str, weather:str, tts=True)-> str:
    """Trigger the alarm which announces through text to speech
    the briefing for whatever the alarm specifies such as weather, news etc"""
    for alarm in alarms:
        if alarm["title"] == alarm_name:
            alarm["content"] = "This alarm has been triggered"
    if tts:
        tts_request(alarm_name + ". ")
    news_title, news_content = get_news()
    stats_title, stats_content = get_covid_news()
    if weather is not None:
        #Announce Weather
        if tts:
            tts_request(get_forecast("Exeter"))
    if news is not None:
        #Announce News
        if tts:
            tts_request("here is your news. "
                        + news_title
                        + news_content.split("http")[0]
                        + ". "
                        + stats_title
                        + stats_content)
    if news is None and weather is None:
        if tts:
            tts_request("You have no briefings right now")
            notifications.insert(0,{"title":"Alarm Notification", "content":news_content})
    return "Passed"

def schedule_alarm(alarm_name:str, alarm_datetime:str, news:str, weather:str)-> str:
    """When the sumbit button is clicked, add the alarm to the alarms column and
    schedule an alarm that will be triggered when the selected date is reached"""
    formatted_date = datetime.strptime(alarm_datetime, '%Y-%m-%dT%H:%M')
    if not(alarm_datetime == "") and ((formatted_date-datetime.utcnow()).total_seconds() > 5):
        alarm_exists = False
        for alarm in alarms:
            if alarm["title"] == alarm_name:
                alarm_exists = True
                break
        if not alarm_exists:
            if news == "news":
                news_answer = "Yes"
            else:
                news_answer = "No"
            if weather == "weather":
                weather_answer = "Yes"
            else:
                weather_answer = "No"
            alarms.append({"title":alarm_name, "content":"This alarm will be triggered at: "
                           + str(alarm_datetime).replace("T"," ") + "\nNews Briefing: "
                           + news_answer + "\nWeather Briefing: "
                           + weather_answer})
            scheduler.add_job(id = alarm_name,
                              func=trigger_alarm,
                              args = [alarm_name, news, weather],
                              trigger="date",
                              run_date=formatted_date,
                              replace_existing=True)
    return "Passed"

def tts_request(announcement:str):
    """Play an announcment as audio through text to speech"""
    engine = pyttsx3.init()
    engine.say(announcement)
    engine.runAndWait()

def get_forecast(city_name:str="Exeter")-> str:
    """Get the description and temperature of the location specified in the parameters"""
    url = "http://api.openweathermap.org/data/2.5/weather?q="+AREA_NAME+"&appid=" + WEATHER_API_KEY
    response = requests.get(url)
    weather_data = response.json()
    if weather_data["cod"] != "404" and weather_data["cod"] != "401":
        current_temperature = int(round(weather_data["main"]["temp"] - 273.15, 0))
        weather_description = (weather_data["weather"])[0]["description"]
        return "The forecast in " +(
            city_name + " is " + str(weather_description)) + (
                ". The temperature is " + str(current_temperature))+ (" degrees celsius")
    return "We could not find the forecast for your location"

def get_covid_news()-> str:
    """extract covid stats from the UK COVID-19 API and return a sentence including the stats"""
    try:
        formatted_date = datetime.strptime(covid_data[0]["date"], '%Y-%m-%d')
        i = random.randint(0,1)

        if i == 0:
            if str(covid_data[1]["newDeathsByDeathDate"]) == "None":
                new_deaths = "0"
            else:
                new_deaths = str(covid_data[1]["newDeathsByDeathDate"])
            return "COVID-19 Statistics","Since "+(
                str(formatted_date.strftime("%A")
                    +", there have been "
                    +str(covid_data[1]["newCasesByPublishDate"])
                    +" new COVID-19 cases and " + new_deaths
                    +" new deaths in "+AREA_NAME))
        return "COVID-19 Statistics", "The R value in " + (
                AREA_NAME + " is ") + str(covid_data[1]["cumDeaths28DaysByDeathDateRate"])
    except IndexError as exception:
        logging.error("INDEX ERROR: %s", str(exception))
        return "Failed"

def get_news()-> str:
    """Extract the latest news articles from the news API and
    return the title and content of a random article"""
    try:
        yesterdays_date = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
        url = "http://newsapi.org/v2/everything?q="+NEWS_TOPIC+"&from="+(
            yesterdays_date + "&sortBy=publishedAt&apiKey=" + NEWS_API_KEY)
        response = requests.get(url)
        news_data = response.json()
        #Pick a random article and return the title
        #filter the articles first for only articles that are in english
        articles = news_data["articles"]
        filtered_articles = list(filter(lambda x: x["title"].isascii(), articles))
        i = random.randint(0,len(filtered_articles)-1)
        return str(filtered_articles[i]["title"]), str(filtered_articles[i]["url"])
    except RuntimeError as exception:
        logging.error("RUNTIME ERROR: %s", str(exception))
        return "Failed"

def test_program() -> None:
    """Run tests on each function to make sure they successfully complete their tasks"""
    print("RUNNING TESTS")
    assert "Passed" in schedule_notification(), "schedule_notification test: FAILED"
    assert "Passed" in remove_notifiction("Test"), "remove_notifiction test: FAILED"
    assert "Passed" in remove_alarm("Test"), "remove_alarm test: FAILED"
    assert "Passed" in trigger_alarm("Test", "news", "weather", False), "trigger_alarm test: FAILED"
    assert "Passed" in schedule_alarm("Test",
                                      "2020-12-04T11:05",
                                      "news", "weather"),"schedule_alarm test: FAILED"
    assert not "We could not find the forecast for your location" in get_forecast(
        "Exeter"),"get_forecast test: FAILED"
    assert not"Failed" in get_covid_news(), "get_covid_news test: FAILED"
    assert not"Failed" in get_news(), "get_news test: FAILED"
    return True

if __name__ == '__main__':
    #Create logging file
    logging.basicConfig(filename='sys.log',
                        filemode='w',
                        level=logging.DEBUG, format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    try:
        test_program()
        notifications.clear()
        alarms.clear()
        #Add starting notifications
        notifications.append({"title":"Weather",
                          "content":get_forecast("Exeter")})
        n_title, n_content = get_news()
        notifications.append({"title":n_title,
                          "content":n_content})
        s_title, s_content = get_covid_news()
        notifications.append({"title":s_title,
                          "content":s_content})
        #Schedule news notifications
        scheduler.add_job(func=schedule_notification,
                          trigger="interval",
                          seconds=60,
                          max_instances = 10)
        #Schedule daily tests
        scheduler.add_job(func=test_program, trigger="cron", hour="00", minute="00", second = "00")
        scheduler.start()
        print("ALL TESTS PASSED")
        logging.info("ALL TESTS PASSED")
        app.run()
    except AssertionError as exception:
        print("TESTING FAILED, ERROR MESSAGE: " + str(exception))
        logging.error('TESTING FAILED, ERROR MESSAGE: %s', str(exception))
