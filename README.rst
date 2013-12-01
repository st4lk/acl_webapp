ACL async application
=====================

Application with permissions system (ACL). Built with python, tornado, mongodb, motor.


Supports
--------

- python 2.7


Installation
------------

- install mognodb: [http://www.mongodb.org/downloads](http://www.mongodb.org/downloads) (tested on 2.4.8)
- start mongod process
- clone this repo
- install dependencies:
    
    pip install -r requirements.txt

- start local server (`--debug=True` will cause debug mode):

    python app.py

- access http://127.0.0.1:8888/
