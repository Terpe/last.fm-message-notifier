import requests
import re
import subprocess
import sched
import time
import logging


#logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.DEBUG)


class inboxChecker:
    

    def __init__(self, Username, Password):
        s = requests.Session()
        s.headers.update({'User-agent': 'Mozilla/5.0'})
        url = "https://secure.last.fm/login"
        csrf = s.get(url).cookies['csrftoken']  
        payload = dict(username=Username, password=Password, csrfmiddlewaretoken=csrf, next='/inbox')
        s.headers.update({'Referer': 'https://secure.last.fm/login'})
        print(s.headers)
        p = s.post(url, payload)
        if p.ok:
            self.FMsession = s
        else:
            ## to do: Exception....
            print("Failed to login. Reason:", p.reason)

         
    def poll(self):
        p = self.FMsession.get('https://www.last.fm/inbox')
        m = re.search("inbox-message--unviewed", p.text)
        try:
            if m.group(0) == "inbox-message--unviewed":

                return True
        except AttributeError:

            return False
           
    def notify(self):
         notification = """
         display notification "You have new message on Last.fm." with title "Last.fm message notifier"
         """
         subprocess.call("osascript -e '{}'".format(notification), shell=True)











       






if __name__ == "__main__":
    __main__()

