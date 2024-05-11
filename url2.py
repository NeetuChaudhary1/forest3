base_url = 'https://developers.google.com/maps/documentation/maps-static'
location = 'longitude,latitude'  # Replace with actual longitude and latitude
zoom_level = '12'  # Adjust the zoom level as needed
image_size = '640x480'  # Adjust the image size as needed
access_token = 'AIzaSyCCIqI5BAzanXQDK9Vvat4KZIXkXvQpUvI'

url = f'{base_url}{location},{zoom_level}/{image_size}?access_token={access_token}'
print(url)

https://maps.googleapis.com/maps/api/js?key=AIzaSyCCIqI5BAzanXQDK9Vvat4KZIXkXvQpUvI
