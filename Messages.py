from ctypes import sizeof
import imaplib
import email
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys
from memory_profiler import profile
load_dotenv()

import email.header

def decode_mime_words(s):
    return u''.join(
        word.decode(encoding or 'utf8') if isinstance(word, bytes) else word
        for word, encoding in email.header.decode_header(s))

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
N = 1000

# create an IMAP4 class with SSL, use your email provider's IMAP server
def getNumberOfMessages():
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate    
    try:
        imap.login(username, password)
    except Exception as e:
        print(e)
        return
        # sys.exit(1)

    # use imap.list() to get the list of mailboxes
    
    # for i in imap.list()[1]:
    #     print(i)
    # return
    status, messages = imap.select("INBOX")

    # total number of emails
    messages = int(messages[0])

    print("No of Messages: ",messages)
    return messages
# @profile
def getMessages(n_start, n_end, records):
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
    
    # for i in imap.list()[1]:
    #     print(i)
    # return
    status, messages = imap.select("INBOX")

    # total number of emails
    messages = int(messages[0])

    # print("No of Messages: ",messages)
    # records = []
    for i in range(messages-n_start, messages-n_end, -1):    
        res, msg = imap.fetch(str(i), '(BODY.PEEK[])')
        print("Getting messages no: ",messages-i)
        
        recordText = ""

        for response in msg:  
            try:              
                if isinstance(response, tuple):            
                    record=dict()
                    msg = email.message_from_bytes(response[1])   
                    for j in columns:
                        if isinstance(msg[j], str):         
                            
                            record[j.replace("-", "")] = email.header.decode_header(msg[j])[0][0]
                        elif msg[j]:
                            record[j.replace("-", "")] = email.header.decode_header(msg[j].__str__())[0][0]
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
                                recordText+=part.get_payload(decode=True)
                            elif content_type == "text/html":
                                soup = BeautifulSoup(part.get_payload(), features="html.parser")
                                for script in soup(["script", "style"]):
                                    script.extract()
                                text = soup.get_text()                            
                                lines = (line.strip() for line in text.splitlines())                            
                                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))                            
                                text = '\n'.join(chunk for chunk in chunks if chunk)  
                                if isinstance(text, str):
                                    recordText+=text
                                else:
                                    print("Some data was not decoded properly")
                                    # recordText+=text.__str__()
                            elif  content_type == "text/plain":
                                recordText+=part.get_payload(decode=True)
                        # print("="*100)            
                    else:
                        try:            
                            body = msg.get_payload(decode=True)
                            soup = BeautifulSoup(body, features="html.parser")
                            for script in soup(["script", "style"]):
                                script.extract()
                            text = soup.get_text()                            
                            lines = (line.strip() for line in text.splitlines())                            
                            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))                            
                            text = '\n'.join(chunk for chunk in chunks if chunk)
                            recordText+=text.replace('\n', '\r\n')
                        except Exception as e:
                            print(e)        
                    # print(recordText)
                    record['Time'] = record["Date"][16:25]
                    record['Day'] = record["Date"][0:3]
                    record['ShortDate'] = record["Date"][5:16]
                    record["MessageText"] = recordText.replace('\n', '\r\n')
                    record["Subject"] = email.header.decode_header(record["Subject"])[0][0]
                    records.append(record)

                    # print(record["Subject"])

            except imap.abort:
                # imap.login(username, password)
                print("Imap is aborted")
                break
            except Exception as e:
                print(e)    
                # imap.login(username, password)
                print(sys.getsizeof(records))
            # print("="*100)

    imap.close()
    imap.logout()
    # print("Total size",sys.getsizeof(records))
    # print("Got all the Messages")
    # return records
# try:
#     (getMessages(7,9, []))
# except Exception as e:
#     print(e)
# print(getMessages)