from argparse import ArgumentParser
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
from os.path import basename

import requests
import base64
import xlsxwriter
import smtplib
import datetime


def get_report_from_api(jira_domain, project, user, password):
    print('get_report_from_api')
    credentials = encode_credentials(user, password)
    headers = {
        'authorization': 'Basic ' + credentials,
        'content-type': 'application/json',
        'cache-control': 'no-cache'
    }
    url = 'https://' + jira_domain + '.atlassian.net/rest/api/2/search?jql=project=' + project + '&maxResults=100'
    response = requests.get(url, headers=headers)
    print('status_code ' + str(response.status_code))

    report = response.json()

    return report


def encode_credentials(user, password):
    print('encode_credentials')
    credentials = user + ':' + password
    encoded = base64.b64encode(credentials.encode())
    return encoded.decode()


def write_to_excel(filename, issues, filter):
    print('write_to_excel')
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()

    worksheet.write(0, 0, 'Project')
    worksheet.write(0, 1, 'Task')

    rows = 1
    for issue in issues:
        key = issue['key']
        fields = issue['fields']

        if filter(issue):
            summary = fields['summary']
            project = fields['project']

            project_key = project['key']

            worksheet.write(rows, 0, project_key)
            worksheet.write(rows, 1, '[' + key + ']' + summary)

            rows = rows + 1

    workbook.close()


def send_email(sender, password, to, subject, file):
    print('send_email')
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    with open(file, "rb") as fil:
        ext = file.split('.')[-1:]
        attached_file = MIMEApplication(fil.read(), _subtype=ext)
        attached_file.add_header('content-disposition', 'attachment', filename=basename(file))
        msg.attach(attached_file)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(sender, password)
    server.sendmail(sender, to, msg.as_string())
    server.close()


def get_name_prefix(email):
    print('get_name_prefix')
    now = datetime.datetime.now()
    month = now.month
    year = now.year

    email_tokens = email.split('@')
    name = email_tokens[0]
    name_tokens = name.split('.')

    if len(name_tokens) == 2:
        user_name = name_tokens[1] + '.' + name_tokens[0]
    else:
        user_name = name

    return 'report-' + str(month) + '-' + str(year) + '-' + user_name


def filter_issue(issue):
    fields = issue['fields']
    timespent = fields['timespent']
    return timespent is not None


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-domain", "--domain", dest="JIRA_DOMAIN")
    parser.add_argument("-pr", "--project", dest="PROJECT")
    parser.add_argument("-e", "--email", dest="EMAIL")
    parser.add_argument("-p", "--password", dest="PASSWORD")
    parser.add_argument("-t", "--to", dest="TO")

    args = parser.parse_args()

    JIRA_DOMAIN = args.JIRA_DOMAIN
    PROJECT = args.PROJECT
    EMAIL = args.EMAIL
    PASSWORD = args.PASSWORD
    TO = args.TO

    report = get_report_from_api(JIRA_DOMAIN, PROJECT, EMAIL, PASSWORD)

    issues = report['issues']

    name_prefix = get_name_prefix(EMAIL)
    file_name = name_prefix + '.xlsx'
    subject = name_prefix

    write_to_excel(file_name, issues, filter_issue)

    send_email(EMAIL, PASSWORD, TO, subject, file_name)
