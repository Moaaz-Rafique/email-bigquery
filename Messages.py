import imaplib
import email
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
load_dotenv()

# account credentials
username = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
imap_server = os.getenv("IMAP_SERVER")

# use your email provider's IMAP server, you can look for your provider's IMAP server on Google
# or check this page: https://www.systoolsgroup.com/imap/
# for office 365, it's this:


columns = ['Message-ID',
           'Delivered-To', 
           'Received',            
           'From', 
           'To', 
           'Subject',
           'Cc', 
           'Date', 
           'Time',
           'Day',
           'ShortDate',
           'Feedback-ID', 
           'X-Google-Smtp-Source', 
           'X-Received', 
           'ARC-Seal', 
           'MIME-Version', 
           'Content-Type', 
           'Content-Transfer-Encoding', 
           'ARC-Message-Signature', 
           'ARC-Authentication-Results', 
           'Return-Path',         
           'Received-SPF', 
           'Authentication-Results', 
           'DKIM-Signature', 
           'X-SES-Outgoing'
        ]
# for i in columns:
#     print(i.replace("-", ""))

# print([i.replace("-", "") for i in columns])

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

# number of top emails to fetch
N = 1

# create an IMAP4 class with SSL, use your email provider's IMAP server


def getMessages():
    # select a mailbox (in this case, the inbox mailbox)
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate    
    try:
        imap.login(username, password)
    except Exception as e:
        print(e)
        return
        # sys.exit(1)

    # use imap.list() to get the list of mailboxes
    
    for i in imap.list()[1]:
        print(i)
    # return
    status, messages = imap.select("INBOX")

    # total number of emails
    messages = int(messages[0])

    print("No of Messages: ",messages)
    records = []
    for i in range(messages, 0, -1):    
        res, msg = imap.fetch(str(i), '(BODY.PEEK[])')
        print("Getting messages no: ",str(i))
        
        recordText = ""

        for response in msg:                
            if isinstance(response, tuple):            
                record=dict()
                msg = email.message_from_bytes(response[1])   
                for j in columns:
                    if isinstance(msg[j], str):         
                        
                        record[j.replace("-", "")] = msg[j]
                    elif msg[j]:
                        record[j.replace("-", "")] = msg[j].as_string()
                    else:
                        record[j.replace("-", "")] = ""
                    # print(j.replace("-", "")+": ", record[j.replace("-", "")])
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True)
                        except Exception as e:
                            print(e)
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            ("printing part ")
                        elif "attachment" in content_disposition:
                            recordText+=part.get_payload()
                        elif content_type == "text/html":
                            soup = BeautifulSoup(part.get_payload(), features="html.parser")
                            for script in soup(["script", "style"]):
                                script.extract()
                            text = soup.get_text()                            
                            lines = (line.strip() for line in text.splitlines())                            
                            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))                            
                            text = '\n'.join(chunk for chunk in chunks if chunk)                            
                            recordText+=text
                        elif  content_type == "text/plain":
                            recordText+=part.get_payload()
                    # print("="*100)            
                else:
                    try:            
                        body = msg.get_payload(decode=True).decode()
                        soup = BeautifulSoup(body, features="html.parser")
                        for script in soup(["script", "style"]):
                            script.extract()
                        text = soup.get_text()                            
                        lines = (line.strip() for line in text.splitlines())                            
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))                            
                        text = '\n'.join(chunk for chunk in chunks if chunk)
                        recordText+=text
                    except Exception as e:
                        print(e)        
                # print(recordText)
                record['Time'] = record["Date"][16:25]
                record['Day'] = record["Date"][0:3]
                record['ShortDate'] = record["Date"][5:16]
                record["MessageText"] = recordText
                records.append(record)
            # print("="*100)

    imap.close()
    imap.logout()
    print("Got all the Messages")
    return records
# (getMessages())
# print(getMessages)