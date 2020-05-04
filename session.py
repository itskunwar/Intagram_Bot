import requests
import json
import credentials

Base_url = 'https://www.instagram.com/'
Login_url = Base_url + 'accounts/login/ajax/'
Username = credentials.test_insta_id
Pw = credentials.test_insta_pw
User_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'

session = requests.Session()
session.headers = {'user-agent':User_agent}
session.headers.update({'Referer':Base_url})

req = session.get(Base_url)
session.headers.update({'X-CSRFToken':req.cookies['csrftoken']})
login_data = {'username': Username, 'password':Pw}
login = session.post(Login_url, data = login_data, allow_redirects = True)
session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
cookies = login.cookies
login_text = json.loads(login.text)

print(login_text)
