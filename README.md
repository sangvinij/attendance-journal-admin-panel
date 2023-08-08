# CRM Backend

## Navigation
* ***[Software version](#software-version)***
* ***[Getting started](#gerring-started)***
* ***[Creating superuser](#creating-superuser)***
* ***[Using the api](#using-the-api)***
* ***[Database administration](#database-administration)***
* ***[Running black](#running-black)***
* ***[Running tests](#running-tests)***

## Software versions

- python:3.11.3
- PIP_VERSION:23.1.2
- POETRY_VERSION:1.5.1

## Getting started

To get started with this project, follow the steps below:
1. Install [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) on your computer if they are not already installed.
2. Clone the repository to your local machine.
3. Navigate to the root directory of the project.
4. configure `.env` file by assigning values to the variables defined in `.env.sample`
 - ***NOTE: Variables values provided in `.env.sample` for MSSQL should be changed in `.env` file in future for correct synchronization of your application with internal CRM system.***
5. In the project directory, run `docker-compose up --build` to start the services.

After completing these steps, the project will be running and available at `http://localhost:8000/`.

## Creating superuser

If you already followed the **[Getting started](#getting-started)** section steps, superuser will be automatically created in webapp container with the following credentials:
```
{username: Iteen.Admin}
{password: Admin1Admin1}
```
This superuser can be used to get access to the django admin panel while the project is launched in containers.
If you want to create superuser locally you can also see how to do it in  **[Running tests](#running-tests)** section below.

## Using the API

The project provides the following endpoints:

- api/docs/ - info by project
- auth/users/ - endpoint for creating a new user or getting list of users.
- auth/users/me/ - endpoint for getting information about the current user.
- auth/token/login/ - endpoint for getting token.
- auth/token/logout/ - endpoint for deleting token.
- auth/token/logoutall/ - endpoint for deleting all users's tokens.

To use these endpoints, follow these steps:

1. Create a new user by sending a POST request to the `auth/users/` endpoint. In the request body, include the following data:

```
{
    "username": "your_username",
    "password": "your_password"
}
```


2. Get a pair of tokens by sending a POST request to the `auth/token/login/` endpoint. In the request body, include the following data:

```
{
    "username": "your_username",
    "password": "your_password"
}
```


3. Use an access token to access protected endpoints. To do this, add an `Authorization` header with the value `Token <token>` to each request.
For example:

    `curl -H "Authorization: Token <token>" http://localhost:8000/auth/users/me/`

4. Get information about the current user by sending a GET request to the `auth/users/me/` endpoint with the user's token in the Authorization header like in the example above.

5. Get list of all the users by sending a GET request to the `auth/users/` with the admin's token.

6. Delete your token by sending a POST request to the `auth/token/logout/` endpoint with the user's token in the Authorization header.

7. Delete all user's tokens by sending a POST request to the `auth/token/logoutall/` endpoint with the user's refresh token in the Authorization header.


## Database administration

To administer the database, you can use pgAdmin, which runs in a separate container. To access pgAdmin, follow these steps:

1. Open a browser and go to `http://localhost:5050/`.
2. Enter the login and password from your `.env` file to log in to pgAdmin.
3. Create a new connection to the necessary database
4. Connect to the database and perform the necessary operations.


## Running black

To check and run code reformating you should navigate to the root directory and ensure that virtual environment is activated:

1. Run `poetry shell` to activate environment if it's not active yet;
2. Run `black . --check` to check if the code needs to be formatted;
3. Run `black .` to reformat the code;


## Running tests
 
**NOTE: Before runing tests, your mssql settings in `.env` file should be configured in a special way (cause your mssql variables in env file are used for synchronization with CRM system, thats why for tests you should choose your own database). Example of settings you can find below:**
```
MSSQL_DATABASE_USERNAME=sa
MSSQL_DATABASE_PASSWORD=6PvqdaM11D #The password must be at least 8 characters long and contain characters from three of the following four sets: Uppercase letters, Lowercase letters, Base 10 digits, and Symbols.
MSSQL_DATABASE_NAME=master
# Use the following value if you are going to start tests inside the webapp container.
MSSQL_DATABASE_HOST=iteen2.mssql
# Use the following value if you are going to start tests with application launched on local machine.
MSSQL_DATABASE_HOST=localhost
```
***Master database will be by defauld in SQL Server that is running inside the container. We can use it for tests, but you can create another database and use it for tests, if it's neccessary.***

***If you want to run all tests inside the container follow the next steps:***
1. Make sure that points 1-4 from ***[Getting started](#getting-started)*** section are already completed.
2. Configure MSSQL settings in `.env` file as mentioned above.
3. Run `docker compose up --build` command.
4. As soon as all containers started, use the command to enter the webapp container:
```docker exec -it iteen2.webapp bash ```
5. After you entered the webapp container use ```pytest``` command to launch tests. 



***If you want run tests and launch the application on local machine, follow the next steps:***
1. Make sure that repository is already cloned on your computer, docker is launched, images already built and are ready for use and containers are not started yet;
2. Navigate to the root derictory of the project;
3. Configure `.env` file by assigning values to the variables defined in `.env.sample`;
 ***use mssql settings mentioned above and additionaly set in PRIMARY_DATABASE_URL configuration for your local database (for example PRIMARY_DATABASE_URL=postgres://admin:admin@localhost:5432/testbase)***
4. Use ```poetry shell``` command to activate virtual environment;
5. Use ```poetry install``` command to install all dependencies;
6. Use ```docker compose up mssql_db``` to start mssql container for future tests.
7. Use ```python project/manage.py migrate``` to apply all migrations;
8. Use ```python project/create_default_db_data.py``` to create default superuser in your database with credentials:
```
{username: Iteen.Admin}
{password: Admin1Admin1}
```
9. Use ```python project/manage.py runserver```
10. Use ```pytest``` command in console to start tests (**NOTE:** ***If you will try to put the command in another console, make sure that virtual environment is active*** - *point 4* ***of the current instruction***).
