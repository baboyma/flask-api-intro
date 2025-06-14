# Importing required packages
import requests
import json

# Composing a payload for API
payload = {'text': 'The beauty of the world is greatly dependent on the eyes seeing it.'}

# Defining content type for our payload
headers = {'Content-type': 'application/json'}

# Sending a post request to the server (API)
response = requests.post(url="http://127.0.0.1:5000/api/text", data=json.dumps(payload), headers=headers)

# Printing out the response of API
print(response.text)