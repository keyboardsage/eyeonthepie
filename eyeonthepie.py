#!/usr/bin/python3
'''
Author: Alwyn Malachi Berkeley (Keyboard Sage)
Date: Sat 15 Apr 2023 11:07:22 AM EDT

This application will connect to the Google Gmail API, peruse all the emails in the inbox, and
save all the sender email addresses to a file.

For the application to work you must have:
1. A valid set of credentials setup in console.cloud.google.com which basically requires
creating a project, navigating to APIs & Services > Library to add the Gmail API as well as
APIs & Services > Credentials to setup OAuth2 authentication for a Desktop application. The
client_secret.json file needed to run this program and interact with the Gmail API can be
downloaded from there. Rename that file ".eyeonthepie_client_secret.json" and place it in
your $HOME directory.
2. The required dependencies which can be installed easily through pip3 like so:
$ pip3 install -r requirements.txt

Example run:
    $ ./eyeonthepie.py -c 100 -f `pwd`/client_secret.json
'''
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import argparse

MAX_EMAILS_TO_READ = 5000
CLIENT_SECRET_FILE = ""

# Set up the Gmail API client
def get_gmail_service():
    creds = None

    # Scopes for accessing Gmail API
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']

    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, scopes)
    creds = flow.run_local_server(port=0)

    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

# Get all the sender email addresses from the inbox up to max_emails
def get_sender_addresses(service, max_emails=5000):
    print ("This may take a while", end = '') # Status

    sender_addresses = []
    email_count = 0
    query = 'is:all'
    request = service.users().messages().list(userId='me', q=query, maxResults=500)
    while request is not None and email_count < max_emails:
        response = request.execute()
        messages = response.get('messages', [])

        for message in messages:
            if email_count >= max_emails:
                break

            msg = service.users().messages().get(userId='me', id=message['id'], format='metadata', metadataHeaders=['From']).execute()
            from_header = msg['payload']['headers'][0]['value']
            sender_addresses.append(from_header)
            email_count += 1

        # Handle pagination
        request = service.users().messages().list_next(request, response)

        # Status
        print(".", end = '')

    print("") # Status dots no longer needed, new line

    return sender_addresses

# Write all the sender email addresses to a file
def write_sender_addresses_to_file(sender_addresses):
    with open('sender_addresses.txt', 'w') as file:
        for address in sender_addresses:
            file.write(f'{address}\n')

# Main
if __name__ == '__main__':
    # Handle the arguments
    parser = argparse.ArgumentParser(description='By default the program reads up to the first 5000 emails and looks for ".eyeonthepie_client_secret.json" in $HOME. Alternatively, you can specify the number of emails to read and the location of the client_secret.json file using optional arguments.')
    parser.add_argument('-c', '--count', type=int, help='Number of emails to read, a positive integer')
    parser.add_argument('-f', '--file', type=str, help='Absolute path to a client_secret JSON file')
    args = parser.parse_args()

    # Set the maximum number of emails to read
    MAX_EMAILS_TO_READ = 5000
    if args.count:
        MAX_EMAILS_TO_READ = args.count

    # Set the path to your client_secret JSON file
    CLIENT_SECRET_FILE = os.environ['HOME'] + '/.eyeonthepie_client_secret.json'
    if args.file:
        CLIENT_SECRET_FILE = args.file

    # Execute
    service = get_gmail_service()
    if service:
        sender_addresses = get_sender_addresses(service, MAX_EMAILS_TO_READ)
        write_sender_addresses_to_file(sender_addresses)
        print('Sender addresses saved to sender_addresses.txt')
    else:
        print('Could not connect to the Gmail API')

