import requests
from bs4 import BeautifulSoup
import datetime

def get_today_contributions(username):
    today = datetime.date.today()
    to_date = today.isoformat()
    
    url = f"https://github.com/users/{username}/contributions?from={to_date}&to={to_date}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    # 오늘 날짜의 <rect> 태그 찾기
    for rect in soup.find_all("rect"):
        if rect.has_attr("data-date") and rect.has_attr("data-count"):
            if rect["data-date"] == to_date:
                print('aaaaaa')
                return int(rect["data-count"])

    return 0

if __name__ == "__main__":
    username = "sdj3261"
    count = get_today_contributions(username)
    print(f"{username}의 오늘 contributions 수: {count}")