#need to install pip3 with sudo apt-get install python3-pip
#use pip3 to install requests module
#click most outside button to boot/reset the ESP32
#syntax for http POST for door

import requests
# Define new data to create
new_data = {
    "action": "openDoor",
    "parameters": {"robotId": "30"}
}

# The API endpoint to communicate with
# This is specific http to our own ESP32 when connected to Nigel hotspot
url_post = "http://192.168.42.87/openDoor"

# A POST request to tthe API
# Each request can only be made with a 30? sec interval if not no feedback
post_response = requests.post(url_post, json=new_data)

# Print the response
post_response_json = post_response.json()
print(post_response_json)
#cant check for substrings direcly from response variable
#convert all to string
check = str(post_response_json)

#match substring of long default msg from return response of call
if "1" in check:
	#turn left
	print("door1")
else:
	#turn right
	print("door2")
