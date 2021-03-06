import os

# The webapp server piggy backs on the thick client.
# Set the path to a thick client installation.
THICK_CLIENT_LOCATION = '/opt/Specify'

# Set the database name to the mysql database you
# want to access.
DATABASE_NAME = os.environ['SPECIFY_DATABASE_NAME']

# The master user login. Use the same values as
# you did setting up the thick client.
MASTER_NAME = 'MasterUser'
MASTER_PASSWORD = 'MasterPassword'

# The Specify web attachement server URL.
WEB_ATTACHMENT_URL = "http://example.com/web_asset_store.xml"

# The Specify web attachment server key.
WEB_ATTACHMENT_KEY = None

# The collection name to use with the web attachment server.
WEB_ATTACHMENT_COLLECTION = None

# Set to true if asset server requires auth token to get files.
WEB_ATTACHMENT_REQUIRES_KEY_FOR_GET = False
