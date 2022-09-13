import imaplib
import email
from email.header import decode_header
from msilib.schema import Error
import webbrowser
import os
import sys
from bs4 import BeautifulSoup


# account credentials
username = "redesign286@gmail.com"
password = "sdefyzciywedvbjg"
# use your email provider's IMAP server, you can look for your provider's IMAP server on Google
# or check this page: https://www.systoolsgroup.com/imap/
# for office 365, it's this:
imap_server = "imap.gmail.com"

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

# number of top emails to fetch
N = 10

# create an IMAP4 class with SSL, use your email provider's IMAP server


def getMessages():
    # select a mailbox (in this case, the inbox mailbox)
    imap = imaplib.IMAP4_SSL(imap_server)
    # authenticate
    try:
        imap.login(username, password)
    except Exception as e:
        print(e)
        sys.exit(1)
    # use imap.list() to get the list of mailboxes
    status, messages = imap.select("INBOX")

    # total number of emails
    messages = int(messages[0])

    print("No of Messages: ",messages)

    for i in range(messages, messages-N, -1):    
        res, msg = imap.fetch(str(i), '(BODY.PEEK[])')
        print("Messages no: ",str(i))
        columns = ['Delivered-To', 'Received', 'X-Google-Smtp-Source', 'X-Received', 'ARC-Seal', 'ARC-Message-Signature', 'ARC-Authentication-Results', 'Return-Path', 'Received', 'Received-SPF', 'Authentication-Results', 'DKIM-Signature', 'DKIM-Signature', 'From', 'To', 'Subject','Cc', 'MIME-Version', 'Content-Type', 'Content-Transfer-Encoding', 'Message-ID', 'Date', 'Feedback-ID', 'X-SES-Outgoing']
        # msg = None
        for response in msg:    
            if isinstance(response, tuple):            
                msg = email.message_from_bytes(response[1])
                # msg = email.message_from_string(data[0][1])
                # print(len(response))
                # print(response[0])
                # j=0
                # while j < len(msg.keys()):
                #     print(msg.keys()[j]+": ",msg[msg.keys()[j]] )
                #     x = input("="*100)
                #     j = j + 1              
                # print("Payload: ", len(msg.get_payload()))  
                # print("Payload-Type: ", type(msg.get_payload()))  
                # # print("Payload-String: ", (msg.__str__()))
                # print("is-multipart", msg.is_multipart())
                # print("content-type", msg.get_content_type())           
                if msg.is_multipart():
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        # print("part content-type: ", content_type)
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True)
                            # print("this is multipart body ",body)
                        except Exception as e:
                            print(e)
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            print("printing part ")
                        elif "attachment" in content_disposition:
                            open(f"payload{i}.html", "w").write(part.get_payload())
                        elif content_type == "text/html":
                            # print("Wrting this------>", part.get_payload())
                            soup = BeautifulSoup(part.get_payload(), features="html.parser")
                            # kill all script and style elements
                            for script in soup(["script", "style"]):
                                script.extract()    # rip it out
                            # get text
                            text = soup.get_text()
                            
                            lines = (line.strip() for line in text.splitlines())
                            
                            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                            
                            text = '\n'.join(chunk for chunk in chunks if chunk)

                            # print(text)
                            open(f"payload{i}.html", "w").write(text)
                        elif  content_type == "text/plain":
                            open(f"payload{i}.html", "w").write(part.get_payload)
                    print("="*100)            
                else:
                    # print("multi? ",msg.is_multipart())
                    try:            
                        body = msg.get_payload(decode=True).decode()
                        # print("body-->", len(body))
                        soup = BeautifulSoup(body, features="html.parser")
                            # kill all script and style elements
                        for script in soup(["script", "style"]):
                            script.extract()    # rip it out
                        # get text
                        text = soup.get_text()
                            
                        lines = (line.strip() for line in text.splitlines())
                            
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                            
                        text = '\n'.join(chunk for chunk in chunks if chunk)
                        open(f"payload{i}.html", "w", encoding="utf-8").write(text)
                    except Exception as e:
                        print(e)
                    print("="*100)
                    
    imap.close()
    imap.logout()