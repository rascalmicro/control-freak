# Send email to one or more recipients
# sender, recipients, subject and body are strings
# Separate multiple recipients with space, comma or semicolon
# Return tuple (status, msg) where status 0 for success, 1 for error
# dsmall 8 Apr 2012
def sendmail(sender, recipients, subject, body):
    import smtplib
    import time
    from email.mime.text import MIMEText
    
    ##### SET UP SMTP SERVER #####
    
    # Fill in details of the SMTP server you will be using
    # If your ISP doesn't provide an SMTP service, you can sign up with gmail
    # These settings are correct for gmail SMTP but you will need to provide
    # a LOCAL_HOST name for your Rascal and your gmail LOGIN and PASSWORD
    HOST = 'smtp.aa.net.uk'     # Outgoing mail server
    PORT = 25                   # Usually 25 or 587
    LOCAL_HOST = 'rascal24'     # Name of your Rascal
    TIMEOUT = 30.0              # Seconds

    # Fill in this section if the SMTP server requires TLS (gmail does)
    USE_TLS = False             # True or False
    LOGIN = ''
    PASSWORD = ''
    
    ##### END OF SET UP #####
    
    # Replace comma or semicolon with a space, then split into a list
    toaddrs = recipients.replace(',', ' ').replace(';', ' ').split()
    print '## sendmail ##', sender, toaddrs, subject
    msg = MIMEText(body)
    msg['From'] = sender
    msg['To'] = ', '.join(toaddrs)
    msg['Subject'] = subject
    msg['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime())
    try:
        server = smtplib.SMTP(HOST, PORT, LOCAL_HOST, TIMEOUT)
        try:
            if USE_TLS:
                server.starttls()
                server.ehlo()
                server.login(LOGIN, PASSWORD)
            resdict = server.sendmail(sender, toaddrs, msg.as_string())
            if len(resdict) == 0:
                result = (0, 'Email sent')
            else:
                sendmail_log(resdict)
                result = (1, 'Can\'t send to some recipients, see log')
        except smtplib.SMTPRecipientsRefused as resdict:
            sendmail_log (resdict)
            result = (1, 'Can\'t send to any recipients, see log')
        except smtplib.SMTPHeloError:
            result = (1, 'The server didn\'t reply properly to the HELO greeting')
        except smtplib.SMTPSenderRefused:
            result = (1, 'The server didn\'t accept the sender')
        except smtplib.SMTPAuthenticationError:
            result = (1, 'The server didn\'t accept the login/password')
        except SMTPDataError:
            result = (1, 'The server replied with an unexpected error code')
        except:
            result = (1, 'Unexpected error')
        server.quit()
    except smtplib.SMTPConnectError:
        result = (1, 'Could not connect to server')
    except:
        result = (1, 'Unexpected error on connect')
    return result

def sendmail_log(resdict):
    print '## sendmail ## Can\'t send to', resdict
