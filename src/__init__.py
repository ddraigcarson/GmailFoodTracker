from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import os
import base64
from datetime import datetime

class Gmail:

    service = None

    def __init__(self):
        # Setup the Gmail API
        SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
        store = file.Storage('credentials.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
            creds = tools.run_flow(flow, store)
        self.service = build('gmail', 'v1', http=creds.authorize(Http()))

    def get_ddraig_message_ids(self):
        print('Getting message IDs')
        results = self.service.users().messages().list(userId='me', maxResults=10, labelIds=['Label_7']).execute()
        messages = results.get('messages', [])

        ids = []
        for message in messages:
            ids.append(message['id'])

        return ids

    def get_messages(self, ids):
        messages = []
        for id in ddraig_message_ids:
            messages.append(gmail.getMessageById(id))
        return messages

    def getMessageById(self, id):
        print('Getting message with ID:' + str(id))
        results = self.service.users().messages().get(userId='me', id=id).execute()
        payload = results['payload']

        date = payload['headers'][2]['value']

        parts = payload['parts']
        attachments = []
        for part in parts:
            if part['mimeType'] == 'image/jpeg':
                attachments.append(part['body']['attachmentId'])

        message = {
            'id': id,
            'date': date,
            'attachment_ids': attachments,
            'attachments': []
        }
        return message

    def get_all_messages_attachments(self, messages):
        print('Getting attachments for messages')
        for message in messages:
            for attachment in message['attachment_ids']:
                result = self.get_attachment_by_id(message['id'], attachment)
                message['attachments'].append(result)
        return messages

    def get_attachment_by_id(self, message_id, attachment_id):
        print('Getting attachment by messageID: ' + message_id + " and attachmentId: " + attachment_id)
        results = self.service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id).execute()
        return results

    def delete_used_images(self, message_ids):
        print("Deleting messages with ids: " + str(message_ids))
        for message_id in message_ids:
            print("Deleting message with id: " + message_id)
            self.service.users().messages().delete(userId='me', id=message_id).execute()


class File:

    ddraig_path = 'D:\\Ddraig'

    def check_for_file(self, file_name):
        return os.path.exists(self.ddraig_path + '\\' + file_name)

    def create_file_name(self, file_name, index):
        file_exists = self.check_for_file(file_name + "-" + str(index) + ".jpeg")
        if file_exists:
            return self.create_file_name(file_name, index+1)
        else:
            return file_name + "-" + str(index) + ".jpeg"

    def write_messages_to_folder(self, messages):
        print("Writing messages to folder")
        for message in messages:
            date_time = datetime.strptime(message['date'], '%a, %d %b %Y %H:%M:%S %z')
            file_name = str(date_time.year) + "-" + str(date_time.month) + "-" + str(date_time.day)
            for attachment in message['attachments']:
                full_file_name = self.create_file_name(file_name, 0)
                self.write_to_folder(attachment, full_file_name)

    def write_to_folder(self, attachment, file_name):
        print("writing file to folder: " + file_name)
        file_data = attachment['data']
        file_data = base64.urlsafe_b64decode(file_data.encode('UTF-8'))
        file_name_with_path = self.ddraig_path + '\\' + file_name
        with open(file_name_with_path, 'wb') as f:
            f.write(file_data)


gmail = Gmail()
ddraig_message_ids = gmail.get_ddraig_message_ids()
ddraig_messages = gmail.get_messages(ddraig_message_ids)
ddraig_messages_with_attachments = gmail.get_all_messages_attachments(ddraig_messages)

file = File()
file.write_messages_to_folder(ddraig_messages_with_attachments)

#gmail.delete_used_images(ddraig_message_ids)

