from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from time import sleep
from tqdm import tqdm

# Function to authorize and get credentials using OAuth2 flow
def authorize_google_tasks(api_name, api_version, scopes, token_file):
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes=scopes)
    creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open(token_file, 'w') as token:
        token.write(creds.to_json())

    return creds

# Function to get or create a task list
def get_or_create_tasklist(service, tasklist_title):
    try:
        # Try to get the task list
        tasklist = service.tasklists().list().execute()
        tasklist_id = next((tl['id'] for tl in tasklist.get('items', []) if tl['title'] == tasklist_title), None)

        if tasklist_id:
            return tasklist_id
    except HttpError as e:
        if e.resp.status != 404:
            raise

    # If the task list doesn't exist, create it
    new_tasklist = service.tasklists().insert(body={'title': tasklist_title}).execute()
    return new_tasklist['id']

# Function to get tasks from a specific task list (including completed tasks) with pagination
def get_tasks(service, tasklist_id, max_results=100):
    all_tasks = []
    next_page_token = None

    while True:
        # Retrieve tasks for the current page
        page_tasks = service.tasks().list(
            tasklist=tasklist_id,
            showCompleted=True,
            showDeleted=True,
            showHidden=True,
            maxResults=max_results,
            pageToken=next_page_token
        ).execute()

        # Add tasks from the current page to the overall list
        all_tasks.extend(page_tasks.get('items', []))

        # Check if there are more pages
        next_page_token = page_tasks.get('nextPageToken')
        if not next_page_token:
            break
            
    return all_tasks

# Function to create tasks in a specific task list with retry
def create_tasks_with_retry(service, tasklist_id, tasks, max_retries=3):
    for task in tqdm(tasks, desc=f"Importing tasks to {tasklist_id}"):
        for retry_count in range(max_retries):
            try:
                # Check for recurring tasks and handle them correctly
                if 'recurrence' in task:
                    # Clear the 'completed' field for recurring tasks
                    task.pop('completed', None)
                    # Insert the recurring task without specifying a due date/time
                    service.tasks().insert(tasklist=tasklist_id, body=task).execute()
                else:
                    # Insert non-recurring tasks
                    service.tasks().insert(tasklist=tasklist_id, body=task).execute()

                # Break out of the retry loop if successful
                break
            except HttpError as e:
                if e.resp.status == 403 and 'quotaExceeded' in str(e):
                    # Quota exceeded, wait for some time and then retry
                    print(f"Quota Exceeded. Retrying in 60 seconds (Attempt {retry_count + 1}/{max_retries})")
                    sleep(60)
                else:
                    # For other errors, raise the exception
                    raise

# Function to create tasks in a specific task list
def create_tasks(service, tasklist_id, tasks):
    create_tasks_with_retry(service, tasklist_id, tasks)

def main():
    # Set the API information
    api_name = 'tasks'
    api_version = 'v1'
    scopes = ['https://www.googleapis.com/auth/tasks']
    token_file_account1 = 'token_account1.json'  # Replace with your token file for account 1
    token_file_account2 = 'token_account2.json'  # Replace with your token file for account 2

    # Authorize and get credentials for the source Google Tasks account
    creds_account1 = authorize_google_tasks(api_name, api_version, scopes, token_file_account1)
    service_account1 = build(api_name, api_version, credentials=creds_account1)

    # Authorize and get credentials for the destination Google Tasks account
    creds_account2 = authorize_google_tasks(api_name, api_version, scopes, token_file_account2)
    service_account2 = build(api_name, api_version, credentials=creds_account2)

    # Get task lists from the source account
    tasklists_account1 = service_account1.tasklists().list().execute().get('items', [])
    print(f"Found {len(tasklists_account1)} task lists in the source account.")

    # Iterate through each task list and get tasks
    for tasklist_account1 in tasklists_account1:
        tasklist_title = tasklist_account1['title']
        tasklist_id_account2 = get_or_create_tasklist(service_account2, tasklist_title)

        tasks_account1 = get_tasks(service_account1, tasklist_account1['id'])
        print(f"\nWorking on task list: {tasklist_title}")
        print(f"Found {len(tasks_account1)} tasks in the source account.")

        # Create tasks in the destination account
        create_tasks(service_account2, tasklist_id_account2, tasks_account1)

    print("\nTasks exported and imported successfully.")

if __name__ == '__main__':
    main()
