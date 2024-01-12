# Google Tasks Transfer Tool <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5b/Google_Tasks_2021.svg/1079px-Google_Tasks_2021.svg.png" alt="Google Tasks icon" width="20" height="20">

A simple Python tool to export and import [Google Tasks](https://mail.google.com/tasks/canvas) items from one Google account to another.

## Features
- [x] Browser login to Google accounts
- [x] Transfer of multiple task lists
- [x] Preserving completion/todo status
- [x] Automatic retry upon hitting API quota
- [ ] Does not support recurrence at the moment as info not available in Google's API

Contribution to this tool is welcomed!

## Usage
### Authorize Credentials
Follow steps in the official [quickstart guide](https://developers.google.com/tasks/quickstart/python#authorize_credentials_for_a_desktop_application) in section _Authorize credentials for a desktop application_. Place the downloaded `credentials.json` in the same directory root of `migrate.py` in this project.

### Install Dependencies
```sh
$ pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Run the Program
Run `python migrate.py` in your shell. A browser page will be opened and you will be prompted to log into your Google account to provide Tasks access. You will need to log in to your source (from which tasks will be exported) and destination (into which tasks will be imported) accounts **in order**. 

Once you're done with logging in to both accounts, the transfer process will commence and you will see terminal outputs similar to the following:
```
(googleapi) ➜ python migrate.py
Please visit this URL to authorize this application: [REDACTED]
Please visit this URL to authorize this application: [REDACTED]
Found 3 task lists in the source account.

Working on task list: My Tasks
Found 300 tasks in the source account.
Importing tasks to VkdYTmo2bUpkSVZKS2dzVw: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 300/300 [04:10<00:00,  1.20it/s]

Working on task list: Work
Found 400 tasks in the source account.
Importing tasks to ZmxWdV9hTEtNSDBPWm51Mw:   6%|███████                                                                                                     | 26/400 [00:12<02:43,  2.28it/s]
Quota Exceeded. Retrying in 60 seconds (Attempt 1/3)
Importing tasks to ZmxWdV9hTEtNSDBPWm51Mw:   6%|███████                                                                                                     | 26/400 [00:23<05:37,  1.11it/s]
...
```

Wait until transfer of each task lists is complete. Log into your Google Tasks on the destination account and verify.

## Acknowledgement

This tool was programmed with the help of OpenAI ChatGPT 3.5.