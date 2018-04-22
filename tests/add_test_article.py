#!/usr/bin/env python3
# Script to easily add new sample articles
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from subprocess import call
from datetime import datetime
import json

def _input_long_text(text_type):
    file_name = "/tmp/temp_" + text_type
    call(["vim", file_name])
    if os.path.isfile(file_name):
        text = open(file_name,"r").read() #Read the file and put the message into a variable
        os.remove(file_name) #Remove the temporary message file
        print(text_type, "of length", len(text), "retrieved")
        return text
    else:
        print("No", text_type, "file found\nExiting")
        exit(1)

try:
    while True:
        print("Fill in info for new article")
        url = input("Url: ")
        title = _input_long_text("title").strip()
        text = _input_long_text("text")
        date = input("YYYY-MM-DD date: ")
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            print("Date in wrong format\nExiting")
            exit(1)
        sources = input("Sources split with ';' character: ").split(";")
        sources = list(filter(lambda x: x != "", sources))
        authors = input("Authors split with ';' character: ").split(";")
        authors = list(filter(lambda x: x != "", authors))
        dict_ = {
            'url': url,
            'title': title,
            'text': text,
            'publish_date': date,
            'sources': sources,
            'authors': authors}
        with open("test_articles.jsonl", 'a') as json_file:
            json_dict = json.dumps(dict_)
            json_file.write(json_dict + "\n")
except KeyboardInterrupt:
    print("Exiting")
