import requests
import json

# Info of the book
# payload = {
#    'isbn': '7418529639871',
#    'title': 'The Book of Meaning',
#    'author': 'Not Sun Tzu'
# }

payload = {
   'isbn': '7418529639872',
   'title': 'The Book of Interpretation',
   'author': 'Not Jonathan Swift',
   'published_date': '2023-10-01'
}

# header of our post request indicating content type to be JSON
headers = {'Content-type': 'application/json'}

# Sending a post request to our API
response = requests.post(url='http://127.0.0.1:5000/api/books',
                        data=json.dumps(payload),
                        headers=headers)

# Printing out the response.
print(response.text)