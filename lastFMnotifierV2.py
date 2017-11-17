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
        '''Create InboxChecker object, login to Last.fm with credentials and prepare requests.Session object for further polling'''
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
         

    def poll(self, interval):
        '''Check inbox and parse html with regex pattern to chceck presence of unread message(s)'''
        # schedule next run via sched.scheduler object - self.timer
        self.timer.enter(int(interval), 1, self.poll, argument=(interval,))
        p = self.FMsession.get('https://www.last.fm/inbox')
        m = re.search("inbox-message--unviewed", p.text)
        try:
            if m.group(0) == "inbox-message--unviewed":
                print('TRUE')
                return True
        except AttributeError:
            print('FALSE')
            return False
           

    def notify(self):
         '''Trigger OSX desktop notification via AppleScript'''
         notificationText = """
         display notification "You have new message on Last.fm." with title "Last.fm message notifier"
         """
         subprocess.call("osascript -e '{}'".format(notificationText), shell=True)



    def startPolling(self, interval):
                '''Trigger periodical polling based on interval argument'''
        self.timer = sched.scheduler(time.time, time.sleep)
        self.timer.enter(int(interval), 1, self.poll, argument=(interval,))
        self.timer.run()



if __name__ == "__main__":
    __main__()

