#!/usr/bin/env python3
"""
Google Drive upload module for the HuggingFace Paper Grabber.

This module handles uploading filtered papers to Google Drive, with support for
both service account and OAuth authentication methods.
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import tempfile

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow


# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive.file']


class GoogleDriveUploader:
    """Handles uploading files to Google Drive."""
    
    def __init__(self, credentials_path: str = None, folder_name: str = "HuggingFace Papers"):
        """
        Initialize the Google Drive uploader.
        
        Args:
            credentials_path: Path to credentials file (service account JSON or OAuth credentials)
            folder_name: Name of the folder to create/use in Google Drive
        """
        self.credentials_path = credentials_path or self._find_credentials_file()
        self.folder_name = folder_name
        self.service = None
        self.folder_id = None
        
    def _find_credentials_file(self) -> Optional[str]:
        """Find credentials file in common locations or create from environment variable."""
        # First check if we have JSON content in environment variable
        service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON')
        if service_account_json:
            try:
                # Parse the JSON and write to a temporary file
                json_data = json.loads(service_account_json)
                temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
                json.dump(json_data, temp_file, indent=2)
                temp_file.close()
                return temp_file.name
            except json.JSONDecodeError:
                print("Warning: GOOGLE_SERVICE_ACCOUNT_JSON contains invalid JSON")
        
        # Then check for file paths
        possible_paths = [
            os.getenv('GOOGLE_DRIVE_CREDENTIALS_PATH'),
            "credentials.json",
            "service_account.json", 
            "google_credentials.json",
            os.path.expanduser("~/.config/google-drive-credentials.json"),
            os.path.expanduser("~/.google/credentials.json")
        ]
        
        for path in possible_paths:
            if path and os.path.exists(path):
                return path
        return None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.credentials_path:
            print("Error: No credentials file found.")
            print("Please provide one of the following:")
            print("1. Service account JSON file")
            print("2. OAuth credentials JSON file")
            print("3. Set credentials_path parameter")
            return False
            
        if not os.path.exists(self.credentials_path):
            print(f"Error: Credentials file not found: {self.credentials_path}")
            raise FileNotFoundError(f"Credentials file not found: {self.credentials_path}")
            
        try:
            # Try service account authentication first
            if self._is_service_account_file(self.credentials_path):
                print("Using service account authentication...")
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path, scopes=SCOPES
                )
            else:
                # Use OAuth flow
                print("Using OAuth authentication...")
                credentials = self._oauth_authenticate()
                
            self.service = build('drive', 'v3', credentials=credentials)
            print("✓ Successfully authenticated with Google Drive")
            return True
            
        except Exception as e:
            print(f"Error during authentication: {e}")
            return False
    
    def _is_service_account_file(self, file_path: str) -> bool:
        """Check if the credentials file is a service account file."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return data.get('type') == 'service_account'
        except:
            return False
    
    def _oauth_authenticate(self) -> Credentials:
        """Handle OAuth authentication flow."""
        creds = None
        token_path = 'token.json'
        
        # Check if we have stored credentials
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        
        return creds
    
    def create_or_get_folder(self) -> bool:
        """
        Create or get the target folder in Google Drive.
        
        Returns:
            bool: True if folder created/found successfully, False otherwise
        """
        if not self.service:
            print("Error: Not authenticated. Call authenticate() first.")
            return False
            
        try:
            # Search for existing folder
            results = self.service.files().list(
                q=f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                self.folder_id = folders[0]['id']
                print(f"✓ Using existing folder: {self.folder_name}")
            else:
                # Create new folder
                folder_metadata = {
                    'name': self.folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                
                folder = self.service.files().create(
                    body=folder_metadata,
                    fields='id'
                ).execute()
                
                self.folder_id = folder.get('id')
                print(f"✓ Created new folder: {self.folder_name}")
            
            return True
            
        except Exception as e:
            print(f"Error creating/getting folder: {e}")
            return False
    
    def upload_files(self, file_paths: List[str], progress_callback=None) -> List[Dict]:
        """
        Upload multiple files to Google Drive.
        
        Args:
            file_paths: List of file paths to upload
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of upload results with file info and status
        """
        if not self.service or not self.folder_id:
            print("Error: Not authenticated or folder not set up.")
            return []
            
        results = []
        
        for i, file_path in enumerate(file_paths):
            if progress_callback:
                progress_callback(i, len(file_paths), file_path)
                
            result = self.upload_file(file_path)
            results.append(result)
            
        return results
    
    def upload_file(self, file_path: str) -> Dict:
        """
        Upload a single file to Google Drive.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            Dict with upload result information
        """
        if not os.path.exists(file_path):
            return {
                'file_path': file_path,
                'success': False,
                'error': 'File not found'
            }
            
        try:
            file_name = os.path.basename(file_path)
            
            # Determine MIME type based on file extension
            mime_type = self._get_mime_type(file_path)
            
            file_metadata = {
                'name': file_name,
                'parents': [self.folder_id]
            }
            
            media = MediaFileUpload(file_path, mimetype=mime_type)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            return {
                'file_path': file_path,
                'file_name': file_name,
                'success': True,
                'file_id': file.get('id'),
                'web_link': file.get('webViewLink'),
                'error': None
            }
            
        except Exception as e:
            return {
                'file_path': file_path,
                'success': False,
                'error': str(e)
            }
    
    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type based on file extension."""
        extension = Path(file_path).suffix.lower()
        
        mime_types = {
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.csv': 'text/csv',
            '.md': 'text/markdown',
            '.html': 'text/html',
            '.xml': 'application/xml'
        }
        
        return mime_types.get(extension, 'application/octet-stream')
    
    def get_folder_link(self, make_public: bool = False) -> Optional[str]:
        """Get shareable link to the Google Drive folder."""
        if not self.folder_id:
            return None
            
        if make_public:
            try:
                # Make folder publicly viewable (optional)
                permission = {
                    'type': 'anyone',
                    'role': 'reader'
                }
                
                self.service.permissions().create(
                    fileId=self.folder_id,
                    body=permission
                ).execute()
                
                print(f"✓ Made folder publicly viewable")
                
            except Exception as e:
                print(f"Warning: Could not make folder public: {e}")
        
        return f"https://drive.google.com/drive/folders/{self.folder_id}"


def upload_papers_to_drive(
    papers_dir: str, 
    credentials_path: str = None,
    folder_name: str = "HuggingFace Papers",
    folder_id: str = None
) -> Tuple[bool, List[Dict]]:
    """
    Upload PDF papers from a directory to Google Drive.
    
    Args:
        papers_dir: Directory containing papers to upload
        credentials_path: Path to Google credentials file
        folder_name: Name of the Google Drive folder (ignored if folder_id is provided)
        folder_id: Specific Google Drive folder ID to upload to
        
    Returns:
        Tuple of (success, results_list)
    """
    if not os.path.exists(papers_dir):
        print(f"Error: Papers directory not found: {papers_dir}")
        return False, []
    
    # Find only PDF files to upload
    file_paths = []
    pdfs_dir = os.path.join(papers_dir, "pdfs")
    if os.path.exists(pdfs_dir):
        for file in os.listdir(pdfs_dir):
            if file.lower().endswith('.pdf'):
                file_path = os.path.join(pdfs_dir, file)
                file_paths.append(file_path)
    
    if not file_paths:
        print("No PDF files found to upload")
        return True, []
    
    print(f"Found {len(file_paths)} PDF files to upload")
    
    # Initialize uploader
    uploader = GoogleDriveUploader(credentials_path, folder_name)
    
    # Authenticate
    if not uploader.authenticate():
        return False, []
    
    # Set folder ID or create/get folder
    if folder_id:
        uploader.folder_id = folder_id
        print(f"✓ Using specified folder ID: {folder_id}")
    else:
        # Create/get folder by name
        if not uploader.create_or_get_folder():
            return False, []
    
    # Upload files with progress
    def progress_callback(current, total, file_path):
        file_name = os.path.basename(file_path)
        print(f"Uploading ({current + 1}/{total}): {file_name}")
    
    results = uploader.upload_files(file_paths, progress_callback)
    
    # Print results summary
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n✓ Successfully uploaded {len(successful)} files")
    if failed:
        print(f"✗ Failed to upload {len(failed)} files:")
        for result in failed:
            print(f"  - {result['file_path']}: {result['error']}")
    
    # Print folder link (don't try to make public when using specific folder ID)
    make_public = False  # Never try to make existing folders public
    folder_link = uploader.get_folder_link(make_public=make_public)
    if folder_link:
        print(f"\n📁 Google Drive folder: {folder_link}")
    
    return len(failed) == 0, results


if __name__ == "__main__":
    # Test the uploader
    import argparse
    
    parser = argparse.ArgumentParser(description="Upload papers to Google Drive")
    parser.add_argument("papers_dir", help="Directory containing papers to upload")
    parser.add_argument("--credentials", help="Path to Google credentials file")
    parser.add_argument("--folder", default="HuggingFace Papers", help="Google Drive folder name")
    
    args = parser.parse_args()
    
    success, results = upload_papers_to_drive(
        args.papers_dir,
        args.credentials,
        args.folder
    )
    
    sys.exit(0 if success else 1)