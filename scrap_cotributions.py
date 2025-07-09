import requests
from bs4 import BeautifulSoup
import datetime

def get_today_contributions(username):
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    today = datetime.date.today().isoformat()

    # 가장 마지막 <rect>가 오늘일 가능성이 높기 때문에 역순 탐색
    for rect in reversed(soup.find_all("rect")):
        if rect.has_attr("data-date") and rect.has_attr("data-count"):
            if rect["data-date"] == today:
                return int(rect["data-count"])

    return 0

if __name__ == "__main__":
    username = "sdj3261"
    count = get_today_contributions(username)
    print(f"{username}의 오늘 contributions 수: {count}")
