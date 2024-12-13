Instructions:


Downloading the client program is enough to use the program. For testing purposes, our Spotify Developers Credential (client id and secret id) are provided, but you may also use your own. If you do want to test, please let us know so that we can start the RDS.


This can be run without Docker if the necessary packages are installed. If not, Docker will work. However, one function will not work properly, specifically function 8 when it opens the browser or Spotify application with the song. This is due to Docker being a container, so it cannot really access browsers. However, as seen in the video, it does work.


For the server side, all the lambda functions are added to an API gateway, where they are all POST requests. When testing, our API gateway should suffice, but if needed, your own API gateway can also be made.




Credits:
Finalproj_auth lambda function is the code from the proj04_auth function that we did for project 4.


Additional Information:
Regarding our video, its looks slightly choppy because we realized that our audio for the first portion was distorted, so we had to re record that portion. Furthermore, towards the end, the laptop being used ended up dying, so there may be a noticeable change in audio, as we had to edit a different segment in.