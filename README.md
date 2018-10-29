Script created with Python 3.
===========

Script requires next dependencies:
===========
1. `python3`
1. `requests`
2. `xlsxwriter`

To run script:
=========== 
1. If you using Gmail go to `https://myaccount.google.com/lesssecureapps` and turn on it, this is needed to sent email
1. Modify `runner.sh`:
    - JIRA_DOMAIN - your company jira domain
    - JIRA_PROJECT_ID - id of project you are want to get report
    - JIRA_USER_EMAIL - email that you used to login to Jira, also this email will be used to send email
    - JIRA_USER_PASSWORD - password from Jira, needed to get access to Jira Api and send email
    - EMAIL_RECIPIENT - email where report will be sent
2. To run script execute: 'sh runner.sh'



