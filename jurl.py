import json

api_key = "AIzaSyBaAt4Omrxfk8lDdeCb6tIK2F1Ae0VkC7Q"
base_url = "https://maps.googleapis.com/maps/api/"

# Constructing the JSON object
json_data = {
    "url": f"{base_url}?key={api_key}"
}

# Converting the JSON object to a string
json_url = json.dumps(json_data)

print(json_url)
