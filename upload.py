from __future__ import print_function
import sys
import glob
import time
import httplib2
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload
from socket import error as SocketError

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/drive'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'FlexData Upload'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main(source, folder, wait=10):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    os.chdir(source)
    
    while True:
        allfiles = sorted(glob.glob('*.txt.gz'))
        
        for f in allfiles[:-1]:
            x = time.time()
            print(f)
            
            file_metadata = { 
                'name' : f, 
                'parents': [folder] }
            try:
                media = MediaFileUpload(f, mimetype='application/gzip')
                file = service.files().create(body=file_metadata,
                    media_body=media,
                    fields='id').execute()
            except SocketError as e:
                print(e)
            else:
                print(file['id'])
                print(time.time()-x)
                media = None
                file = None
                time.sleep(2)
                os.remove(f)
            
        time.sleep(wait)

if __name__ == '__main__':
    source = sys.argv[1]
    folder = sys.argv[2]
    while 1: 
        try:
            main(source, folder)
        except Exception as e:
            print(e)
            
