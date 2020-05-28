# Capstone Project

## Content

## Covered Topics

Capstone project is last project of the `Udacity-Full-Stack-Nanodegree` Course which covers Modeling of Database with `postgres` and `sqlalchemy`, implementation of CRUD operations using `Flask`, automated testing (with `Unittest`), authorization and authentification (with `Auth0`) and lastly deployment (with `Heroku`).

## Start Project locally

Required: [Python 3](https://www.python.org/downloads/)
and [postgres](https://www.postgresql.org/download/) 

To start and run the local development server,

1. Initialize and activate a virtualenv:
2. Install the dependencies:
```
$ pip install -r requirements.txt
```

3. Change database config so it can connect to your local postgres database 
- Here you can see this dict:
 ```python
database_setup = {
    "database_name_production" : "agency",
    "user_name" : "postgres", # default postgres user name
    "password" : "testpassword123", # if applicable. If no password, just type in None
    "port" : "localhost:5432" # default postgres port
}
```

 - Just change `user_name`, `password` and `port` to whatever you choose while installing postgres.
>_tip_: `user_name` usually defaults to `postgres` and `port` always defaults to `localhost:5432` while installing postgres, most of the time you just need to change the `password`.

4. Setup Auth0
 API can be tested by simply taking the existing bearer tokens in `config.py`.

FYI: Here are the steps I followed to enable [authentification](#authentification).

5. Run the development server:
  ```
  $ python app.py
  ```

## API Documentation

Here you can find all existing endpoints, which methods can be used, how to work with them & example responses you´ll get.

I used `POSTMAN` to check the authencity of my endpoints.

### URL

**_https://capstone-udacity-fsnd.herokuapp.com/_**

## Project HighLights

### Authentification

All API Endpoints are decorated with Auth0 permissions. To use the project locally, you need to config Auth0 accordingly

### Auth0 for locally use
#### Create an App & API

1. Login to https://manage.auth0.com/ 
2. Click on Applications Tab
3. Create Application
4. Give it a name like `MyCapstone` and select "Regular Web Application"
5. Go to Settings and find `domain`. Copy & paste it into config.py => auth0_config['AUTH0_DOMAIN'] 
6. Click on API Tab 
7. Create a new API:
   1. Name: `Capstone`
   2. Identifier `Capstone`
   3. Keep Algorithm as it is
8. Go to Settings and find `Identifier`. Copy & paste it into config.py => auth0_config['API_AUDIENCE'] 

#### Create Roles & Permissions

1. Before creating `Roles & Permissions`, you need to `Enable RBAC` in your API (API => Click on your API Name => Settings = Enable RBAC => Save)
2. Also, check the button `Add Permissions in the Access Token`.
2. First, create a new Role under `Users and Roles` => `Roles` => `Create Roles`
3. Give it a descriptive name like `Casting Assistant`.
4. Go back to the API Tab and find your newly created API. Click on Permissions.
5. Create & assign all needed permissions accordingly 
6. After you created all permissions this app needs, go back to `Users and Roles` => `Roles` and select the role you recently created.
6. Under `Permissions`, assign all permissions you want this role to have. 


### Auth0 to use existing API
If you want to access the real, temporary API, bearer tokens for all 3 roles are included in the `config.py` file.

## Existing Roles

They are 3 Roles with distinct permission sets:

1. Casting Assistant:
  - GET /actors (view:actors): Can see all actors
  - GET /movies (view:movies): Can see all movies
2. Casting Director (everything from Casting Assistant plus)
  - POST /actors (create:actors): Can create new Actors
  - PATCH /actors (edit:actors): Can edit existing Actors
  - DELETE /actors (delete:actors): Can remove existing Actors from database
  - PATCH /movies (edit:movies): Can edit existing Movies
3. Exectutive Dircector (everything from Casting Director plus)
  - POST /movies (create:movies): Can create new Movies
  - DELETE /movies (delete:movies): Can remove existing Motives from database

In your API Calls, add them as Header, with `Authorization` as key and the `Bearer token` as value. Don´t forget to also
prepend `Bearer` to the token (seperated by space).

For example: (Bearer token for `Casting Director`)
```js
{
        "Authorization" : "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IkJMdTBfTFhfZlFHd0JXbW5rdjVrQyJ9.eyJpc3MiOiJodHRwczovL2Rldi1teDE2bXV3Yy5hdXRoMC5jb20vIiwic3ViIjoiZ29vZ2xlLW9hdXRoMnwxMTc1OTY5NDk0MjczMTMwOTk0NjciLCJhdWQiOlsiQ2Fwc3RvbmUiLCJodHRwczovL2Rldi1teDE2bXV3Yy5hdXRoMC5jb20vdXNlcmluZm8iXSwiaWF0IjoxNTkwNjg0NDMzLCJleHAiOjE1OTA3NzA4MzMsImF6cCI6IndyNFRCV25MM2dKcXFoVTBaQ0t1bFBza2szQmRRTERTIiwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphY3RvciIsImdldDphY3RvcnMiLCJnZXQ6bW92aWVzIiwicGF0Y2g6YWN0b3JzIiwicGF0Y2g6bW92aWVzIiwicG9zdDphY3RvciJdfQ.mAcqzS5DN3jVUTjVs2Hf7CJiWuSUjgkwov2VenphN7RnmEohmcwyhysLtYK5ODd8UwOzft2lgdyd-I_7Q9wi2OsrL8nfy8JtqWj8UdhMLEGVb9in7Op866Atz8gqXYAkKpxaC8twP5lapUhltN0aC7hEjnUjX6XhFlbL8yIOSH8aEGoymQkyl8x9liAD88PhFyU8EOx3P985qcBdDchxU5JAsr_R1Ixt-8n1313pHKs3mibKRULBVReAf9EI3ZPAl_MJ1VaOXV2_iJqGlC0lhf9wZwv3REFgkAHmqGDd4WnXoK2OPLoKHmyU8yhe9yWd-QKqSGWzomusZKsRC5QmPg"
}
```