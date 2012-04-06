# Send email to one or more recipients
# sender, recipients, subject and body are strings
# Separate multiple recipients with space, comma or semicolon
# Return tuple (status, msg) where status 0 for success, 1 for error
# dsmall 7 Jan 2012
def sendmail(sender, recipients, subject, body):
    import smtplib
    import time
    from email.mime.text import MIMEText
    # Replace comma or semicolon with a space, then split into a list
    toaddrs = recipients.replace(',', ' ').replace(';', ' ').split()
    print '## sendmail ##', sender, toaddrs, subject
    msg = MIMEText(body)
    msg['From'] = sender
    msg['To'] = ', '.join(toaddrs)
    msg['Subject'] = subject
    msg['Date'] = time.strftime("%a, %d %b %Y %H:%M:%S %z", time.localtime())
    s = smtplib.SMTP('smtp.aaisp.net.uk')
    try:
        resdict = s.sendmail(sender, toaddrs, msg.as_string())
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
    except SMTPDataError:
       result = (1, 'The server replied with an unexpected error code')
    except:
       result = (1, 'Unexpected error')
    s.quit()
    return result

def sendmail_log(resdict):
    print '## sendmail ## Can\'t send to', resdict
