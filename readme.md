
# DATA PUSHER Project

## Introduction

This application build to receive data into the app server for an account
and send it across different platforms from that particular account using webhook
URLs.

## Technology Considerations
### Consideration1: Development 
    1. Programming Language                Python
    2. Version                             v3.10
    3. Framework                           Django
    5. IDE                                 Pycharm, Visual Studio Code
    
### Consideration2: Services Design

    1. Database                            sqlite3 

``` bash

├── datapusher
    ├── env 
       ├── account
            ├──migrations
                └──__init__.py
            ├──__init__.py
            ├──admin.py
            ├──apps.py
            ├──models.py
            ├──tasks.py         
            ├──urls.py
            ├──views.py 
       ── datapusher
            ├──__init__.py
            ├──asgi.py
            ├──consumers.py
            ├──settings.py
            ├──urls.py
            ├──wsgi.py
    ├──manage.py
    ├──readme.md
    ├──Dockerfile
    ├──requirements.txt 
```
   
## Setup Instructions
__Steps__

1.  Install Required Packages for Server  
   
        sudo apt-get install python3  
        
        sudo apt-get install python3-pip python3-dev
        
        sudo pip3 install virtualenv
    

2. Django Environment Setup
    
        virtualenv -p python3 env_name 
        
        source env_name/bin/activate
        
        pip install -r requirements.txt

3. Run Server
    
        python manage.py makemigrations     # to migrate all the migrations

        python manage.py migrate            # to migrate all the migrations
        
        python manage.py setup_backend all   # to create default tables and admin creation
                
        python manage.py runserver          # to run the server

4. Run server in docker (optional)
    
        sudo apt-get install docker        

        docker build -t datapusher .          # to build docker image  
  
        docker run -p 8000:8000 datapusher    # to run server using docker
                

5. Run asgi server

         daphne datapusher.asgi:application   # to run asgi server

        
