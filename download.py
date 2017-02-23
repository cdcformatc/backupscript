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
from apiclient.http import MediaIoBaseDownload
from apiclient import errors
from socket import error as SocketError
import io

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
    
def delete_file(service, file_id):
    """Permanently delete a file, skipping the trash.

    Args:
    service: Drive API service instance.
    file_id: ID of the file to delete.
    """
    
    print('Delete file {}.'.format(file_id))
    
    # Potentially raises errors.HttpError (eg:403, 404)
    # Nothing to do about http errors 
    
    service.files().delete(fileId=file_id).execute()
    print('File Deleted.')

def download_file(service, id, localpath):
    print(localpath)
    request = service.files().get_media(fileId=id)
    fh = io.FileIO(localpath, mode='wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
        
def main(dest, folder, limit=0, wait=10, download=True, delete=True):
    # Log in, initialize service
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    
    # Create path
    if not os.path.exists(dest):
        os.mkdir(dest)
    
    check_limit = (limit != 0)
    
    page_token = None
    complete = False
    while not complete:
        # Get files in current page
        response = service.files().list(
            q="'{}' in parents".format(folder),
            fields='nextPageToken, files(id, name)',
            orderBy='modifiedTime',
            pageToken=page_token).execute()
            
        files = response.get('files', [])
        if len(files) == 0:
            print('No files found in {}.'.format(folder))
            complete = True
        
        for file in files:
            name = file.get('name')
            id = file.get('id')
            print('Found file: {} {}.'.format(name, id))
            local_filename = os.path.join(dest, name)
            
            if download:
                download_file(service, id, local_filename)
                
            if delete:
                delete_file(service, id)
                
            if check_limit:
                limit -= 1
                print('{} files left.'.format(limit))
                if limit <= 0:
                    complete = True
                    break
        else:
            print("Finished page.")
            
        # Get next page
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            print('Failed to get next page.')
            complete = True

    print('Download complete.')
    
if __name__ == '__main__':
    dest = sys.argv[1]
    folder = sys.argv[2]
    n=int(sys.argv[3])
    main(dest,folder,limit=n,download=True,delete=True)
