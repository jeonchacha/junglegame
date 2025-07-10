import requests
from bs4 import BeautifulSoup
import datetime

def getContributionCount(githubAccount):
    date = datetime.date.today()

    link = f'http://github.com/users/{githubAccount}/contributions?from={date}&to={date}'
    req = requests.get(link)
    html = req.text

    soup = BeautifulSoup(html, 'html.parser')

    contributionMsg = []
    tooltips = soup.find_all('tool-tip')
    for tooltip in tooltips:
        text = tooltip.get_text(strip=True)
        if "contributions" in text:
            contributionMsg.append(text)

    date = datetime.date.today() - datetime.timedelta(days=1)
    
    day = date.day
    month = date.strftime("%B")

    if 10 <= day <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

    today_string_match = f"{month} {day}{suffix}."

    for entry in contributionMsg:
        if today_string_match in entry:
            return entry

    return today_string_match