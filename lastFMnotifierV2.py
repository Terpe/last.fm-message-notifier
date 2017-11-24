import requests
import re
import subprocess
import sched
import time
import logging


logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
#logging.disable(logging.DEBUG)

Username=''
Password=''



class inboxChecker:
    
    def __init__(self, Username, Password):
        '''Create InboxChecker object, login to Last.fm with credentials and prepare requests.Session object for further polling'''
        self.UnreadMessageFlag = False
        s = requests.Session()
        s.headers.update({'User-agent': 'Mozilla/5.0'})
        url = "https://secure.last.fm/login"
        csrf = s.get(url).cookies['csrftoken']  
        payload = dict(username=Username, password=Password, csrfmiddlewaretoken=csrf, next='/inbox')
        s.headers.update({'Referer': 'https://secure.last.fm/login'})
        p = s.post(url, payload)
        ## it seems that we get 200 even after submitting emptpty strings as user,pass ???
        ## in p.text is already content of inbox. 
        ## TODO: i could use it for the first check. probably create new method 
        ## which implements just html parsing in order to separate parsing  logic from polling logic
        ## parsing logic can also be enhanced in future 
        if p.ok:
            self.FMsession = s
        else:
            ## to do: Exception....
            print("Failed to login. Reason:", p.reason)
         

    def poll(self, interval, Timer=True):
        '''Check inbox and parse html with regex pattern to chceck presence of unread message(s)'''
        p = self.FMsession.get('https://www.last.fm/inbox')
        m = re.search("inbox-message--unviewed", p.text)
        try:
            if m.group(0) == "inbox-message--unviewed" and not self.UnreadMessageFlag:
                ## in case of unread message detected and UnreadMessageFlag was FALSE, new message >>  .notify()
                logging.debug('TRUE')
                self.notify()
                self.UnreadMessageFlag = True
            else: 
                logging.debug('Unread Message, but already notified...')           
        except AttributeError:
            ## "inbox-message--unviewed" is missing, set flag (back) to false
            logging.debug('FALSE')
            self.UnreadMessageFlag = False
        # schedule next run of this method via sched.scheduler object - self.timer
        if Timer:
            self.timer.enter(int(interval), 1, self.poll, argument=(interval,))

            

    def notify(self):
         '''Trigger OSX desktop notification via AppleScript'''
         notificationText = """
         display notification "You have new message on Last.fm." with title "Last.fm message notifier"
         """
         subprocess.call("osascript -e '{}'".format(notificationText), shell=True)


    def startPolling(self, interval):
        '''Trigger periodical polling based on interval argument'''
        self.timer = sched.scheduler(time.time, time.sleep)
        self.poll(interval, Timer=False)
        self.timer.enter(int(interval), 1, self.poll, argument=(interval,))
        self.timer.run()
        

checker = inboxChecker(Username, Password)
checker.startPolling(300)


