
auth_data = {}

API_URLS = (
    'https://secure1.iconcmo.com/api/', 
    'https://secure2.iconcmo.com/api/', 
    'https://secure3.iconcmo.com/api/'
)

api_url = ''

REQUEST_TEMPLATE = { 
    "Auth": { 
        # "Phone": "", 
        # "Username": "", 
        # "Password": "" 
        # OR
        # session: ""
    }, 
    "Request": { 
        "Module": "",   # membership, contributions, etc.
        "Section": "",  # households, members, etc.
        "Action": "",   # create, read, update, delete
        # "Data": {},
        # "Filters": {}
    }     
}

DEFAULT_STATUSES = {
    'Member': 'Active',
    'Newcomer': 'Visitor'
}