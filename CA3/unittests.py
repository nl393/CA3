from main import logging, remove_notifiction,schedule_notification,remove_notifiction,remove_alarm,trigger_alarm,schedule_alarm,get_forecast,get_covid_news,get_news
print("RUNNING TESTS...")
def run_tests() -> None:
    assert "Passed" in schedule_notification(), "schedule_notification test: FAILED"   
    assert "Passed" in remove_notifiction("Test"), "remove_notifiction test: FAILED"
    assert "Passed" in remove_alarm("Test"), "remove_alarm test: FAILED"
    assert "Passed" in trigger_alarm("Test", "news", "weather", False), "trigger_alarm test: FAILED"
    assert "Passed" in schedule_alarm("Test", "2020-12-04T11:05", "news", "weather"), "schedule_alarm test: FAILED"
    assert not("We could not find the forecast for your location") in get_forecast("Exeter"), "get_forecast test: FAILED"
    assert not"Failed" in get_covid_news(), "get_covid_news test: FAILED"
    assert not"Failed" in get_news(), "get_news test: FAILED"
    return True;

try:
    if run_tests():
        print("ALL TESTS PASSED, RUNNING THE MAIN PROGRAM NOW")
        exec(open("main.py").read())
except AssertionError:
    user_input = input("TESTING FAILED, PRESS ENTER TO RUN THE PROGRAM ANYWAY")
    print("RUNNING THE MAIN PROGRAM NOW")
    exec(open("main.py").read())
