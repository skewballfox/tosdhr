from dotenv import dotenv_values
from requests import request, Session
from bs4 import BeautifulSoup, GuessedAtParserWarning
import warnings

warnings.filterwarnings("ignore", category=GuessedAtParserWarning)
# TODO: add code for pulling case data on all cases, but
# filter it down to the cases we have annotations for
class Case(object):
    def __init__(self, case_id: int, description: str):
        self.id: int = case_id
        self.description: str = description
        self.approved_annotations = []
        self.declined_annotations = []


def get_topics():
    output = {}
    s = Session()
    config = dotenv_values()

    # Get the topics page
    response = s.get(
        "https://edit.tosdr.org/topics",
        auth=(config["USER"], config["PASSWORD"]),
    )
    soup = BeautifulSoup(response.content)

    # Get the links to the topic pages
    for topic in soup.select("a[href*=topics]"):
        if topic.text != "[Deprecated]":
            # Get the URL for the topic page
            url = f"https://edit.tosdr.org/{topic.get('href')}"
            # Go to the topic page
            response = s.get(url, auth=(config["USER"], config["PASSWORD"]))
            soup = BeautifulSoup(response.content)
            # Get the links to the case pages
            for case in soup.select("a[href*=cases]"):
                url = f"https://edit.tosdr.org/{case.get('href')}"
                caseID = case.get("href").split("/")[-1]
                output[str(caseID)] = (case.text, topic.text)
    return output
