# citibike_stations

I love the citibike system in New York, but there are times when I walk out the door and there are no bikes in my local station. 
In this repository I am working on scripts to collect, analyze and do real-time reporting of the  citibke availability across stations in the city. 

## Methods

I'm sampling the station availability continously on a raspberry Pi. 
I am requesting the station data every 10 seconds and any new data is added to a dictionary.
I save these to json (~1 Mb) every hour for a week. 
Once this is done I will add it to the repository. 