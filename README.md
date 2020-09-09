# Documentation

## Google API KEY

Get API key:
https://developers.google.com/maps/documentation/javascript/get-api-key
https://console.cloud.google.com/projectselector2/google/maps-apis/overview?supportedpurview=project

For this web app to run, you must acquire a Google Maps API key. The Distance
Matrix API must be enabled. In the terminal window, enter your API key in the
format of 'export API_KEY=[your api key]'

The website will not launch until a valid key is provided.

The API is used to calculate the distances between two given locations.
Once the distance is calculated by the information acquired by the API, the
information is used to determine which of the given locations are the closest
through a function I defined as "closest" under the "optimize" route in application.py.

## Running the Website

Change into the correct directory, and run website with the following terminal commands
/cd project
/cd implementation
export API_KEY=[your api key]
flask run

## Entering Locations

When filling out the location field in the add task forms, either the street address
or valid name is an acceptable input. A name is valid if it is recognized by Google Maps.
For example "Leet Oliver Memorial Hall" or "12 Hillhouse Ave New Haven, CT 06511" would
be valid inputs for the same location. However, "Shipping Center" for example could not
be used in place of "250 Church St New Haven, CT 06510" because it is too broad and is not
recognized as any specific location by Google Maps.




