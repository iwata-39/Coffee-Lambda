import os
import json
from google.auth import aws

def get_credentials():
    json_config_info = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    credentials = aws.Credentials.from_info(json_config_info)

    scoped_credentials = credentials.with_scopes([
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/spreadsheets'
    ])

    return scoped_credentials