from selenium import webdriver
import time
from bs4 import BeautifulSoup
import requests
import json
import smtplib
import credentials
from session import session

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'http://www.wikipedia.org/',
    'Connection': 'keep-alive',
}

class InstaBot:
    def __init__(self,username,pw):
    
        self.driver = webdriver.Chrome()
        try:
            self.driver.get("https://instagram.com")
            time.sleep(3)
            print("Logging In..")
            self.driver.find_element_by_xpath("//input[@name=\"username\"]").send_keys(username)
            self.driver.find_element_by_xpath("//input[@name=\"password\"]").send_keys(pw)
            self.driver.find_element_by_xpath('//button[@type="submit"]').click()
            time.sleep(5)
            print()
            self.driver.find_element_by_xpath("//button[contains(text(), 'Not Now')]").click()
            time.sleep(3)
        except Exception as e:
            print("Oopsie! Something went wrong : ",e)


    def get_friend_unfollowers(self,f_username):
        try:
            print("Getting {}'s profile...".format(f_username))
            self.driver.get("https://instagram.com/{}/".format(f_username))
            time.sleep(3)
            print("Reading Following...")
            self.driver.find_element_by_xpath("//a[contains(@href,'/following')]").click()
            following = self._get_names()
            time.sleep(2)
            print("Reading Followers...")
            self.driver.find_element_by_xpath("//a[contains(@href,'/followers')]").click()
            followers = self._get_names()
            self.unfollowers = [kutte for kutte in following if kutte not in followers]
            print("Unfollowers extracted : ",len(self.unfollowers))
            #for name in self.unfollowers:
                #print(name)
        except Exception as e:
            print(e)


    def _get_names(self):
        
        time.sleep(2)
        try:
            scroll_box = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]/ul/div")
            sugs = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]/div[1]/h4')
            time.sleep(7)
            self.driver.execute_script('arguments[0].scrollIntoView({behavior: "smooth"})', sugs) 
        except:    
            scroll_box = self.driver.find_element_by_xpath("/html/body/div[4]/div/div[2]")
            #print("Else Executed")
            last_ht, ht = 0,1
            while last_ht != ht:
                last_ht = ht
                time.sleep(2)
                ht = self.driver.execute_script("""
                    arguments[0].scrollTo({top:arguments[0].scrollHeight,behavior: 'smooth'});
                    return arguments[0].scrollHeight;""",scroll_box)
        finally:
            links = scroll_box.find_elements_by_tag_name('a')
            names = [name.text for name in links if name.text != '']
            self.driver.find_element_by_xpath("/html/body/div[4]/div/div[1]/div/div[2]/button").click()
            return names


    def get_bad_people(self):
        
            self.bad_people = []
            
            for name in self.unfollowers:
                print(name)
                time.sleep(1)
                r = session.get('https://instagram.com/{}/'.format(name),headers= {'User-agent': 'your bot 0.1'})
                try:
                    soup = BeautifulSoup(r.text,'html.parser')
                    scripts = soup.findAll('script',{'type':'text/javascript'})
                    shared_data = scripts[3].text[21:-1]
                    main_json = json.loads(shared_data)
                    followers = float(main_json['entry_data']['ProfilePage'][0]['graphql']['user']['edge_followed_by']['count'])
                    following = float(main_json['entry_data']['ProfilePage'][0]['graphql']['user']['edge_follow']['count'])
                    try:
                        if following/followers > 0.1:
                            self.bad_people.append('@'+name)
                    except:
                        pass
                except:
                    print(r.status_code)
            print("Bad People Extracted : ",len(self.bad_people))
            for name in self.bad_people:
                print(name)


    def send_message(self):

        print("sending message")
        time.sleep(1)
        try:
            self.driver.get('https://instagram.com/{}/'.format(credentials.insta_f_id))
            time.sleep(2)
            self.driver.find_element_by_xpath("//button[contains(text(), 'Message')]").click()
            time.sleep(2)
            message = "You may consider to unfollow them :\n{}\n".format(self.bad_people)
            self.driver.find_element_by_xpath("//textarea[@placeholder=\"Message...\"]").send_keys(message)
            time.sleep(3)
            #self.driver.find_element_by_xpath("//button[contains(text(), 'Send')]").click()
            print("Message sent")
        except Exception as e:
            print("Unable to send message to {} :".format(credentials.insta_f_id),e)


    def send_email(self,rec_email):
        
        try:
            server = smtplib.SMTP('smtp.gmail.com:587')
            server.ehlo()
            server.starttls()
            server.login(credentials.gmail_id, credentials.gmail_pw)
            message = 'Subject: Unfollowers List\n\nConsider them to Unfollow:\n{}'.format(self.bad_people)
            server.sendmail(credentials.gmail_id,rec_email,message)
            server.quit()
            print("Mail Successfully sent!")
        except Exception as e:
            print("Email failed to send : ",e)


start_time = time.time()             
My_bot = InstaBot(credentials.main_insta_id,credentials.main_insta_pw)
My_bot.get_friend_unfollowers(credentials.insta_f_id)
My_bot.get_bad_people()
My_bot.send_message()
My_bot.send_email(credentials.email_id)
print("Execution Time : {:.2f} secs".format(time.time()-start_time))


