### CA3 - Nicholas Latham

## Deploying the program
	Run main.py

## How to use the program:
	# Alarms
		Alarms can be added by entering a date, a label and checking the briefings that you want to recieve when the alarm is triggered
		You cannot enter a label for an alarm if there is already and existing alarm with the same label
		You must enter a datetime
		You cannot enter a datetime that is less than 5 seconds in the future
		Once all the above conditions are met, you can click submit which will then add the alarm to the alarms column
		The now set alarm will be triggered when the set datetime is met
		When triggered the alarm will announce, through text to speech, the title of the alarm, and the set briefings
		If no briefings were set the alarm will add a news briefing to the notifications column titled "Alarm Notification" when triggered
		Closing an alarm will remove it from the column and cancel the scheudled announcement
	
	# Notifications
		The notifications column is controlled through a scheduled job that adds notifications to the column
		A notification can be one of three types of notificaiton; weather, news, or COVID-19 related news/stats
		The notifications column is scheduled to update every minute
		The scheduled function first adds a weather notification followed by a COVID-19 notification and then the rest of the colum is filled with news notifications
		If an item is removed from the column, upon being triggered, the function will check if the column has a weather notification, if it does not then the weather will be added to the column
		The same process is done for the COVID-19 notification
		If the column has a weather item and a COVID-19 item then a news item is added to the column
		The column has a limit of 5 notifications at once with the exception of when an "Alarm Notification" is added

	# Config File
		The program offers some customisation in the form of a config file in which certain attrtibutes can be edited
		The variables that can be changed are the topic of the news that you recieve and your location

## Prerequisites/Installations
	import logging -------> pip install logging
	import random -------> 
	import json -------> pip install jsonlib
	from datetime import datetime, timedelta -------> pip install DateTime
	from flask import Flask, render_template, request -------> pip install Flask
	from uk_covid19 import Cov19API -------> pip install uk-covid19
	from apscheduler.schedulers.background import BackgroundScheduler -------> pip install apscheduler
	import pyttsx3 -------> pip install pyttsx3
	import requests -------> pip install requests

## Testing the program
	To test the program's functions, run tests.py, if all tests pass main.py will be run
	The tests are designed to measure whether or not the end of the function is reached, if the end of the function is reached without error, it is considered a success
	If one or more tests fail, the program will not execute main.py
	These tests are run routinely at midnight every day

	To test the format of the code, run the pylint_test.py

## Logging
	The program logs all events and stores the information in the file called sys.log
	Information about whether the deplotment tests passed or not and try except error messages are also stored in the log file
	All information is stored with the date and time of the event

## License
	Copyright (c) 2020 Nicholas Latham

	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
