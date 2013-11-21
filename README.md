spam-free-chat
==============

The biggest problem that any chat application has is dealing with spam bots. This is an attempt to build a chat application that has an inherent way of detecting and blocking spam

To run, clone the project (Including the dataset, around 4 MB) and run the following commands before trying to run it  
    #apt-get install python-pip
    #apt-get install python-dev
    #apt-get install libevent-dev
    #pip install gevent-socketio==0.3.5-rc2

Then run 
    $python server.py

and go to ```http://localhost:8080```