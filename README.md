# CRM Backend


## Getting started

To get started with this project, follow the steps below:
1. Install [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) on your computer if they are not already installed.
2. Clone the repository to your local machine.
3. Navigate to the root directory of the project.
4. configure `.env` file by assigning values to the variables defined in `.env.sample`
5. In the project directory, run `docker-compose up --build` to start the services.

After completing these steps, the project will be running and available at `http://localhost:8000/`.

## Creating superuser

To create a superuser, execute the following command:

`docker-compose exec webapp python project/manage.py createsuperuser`

Follow the on-screen instructions to set credentials for the superuser.

Open your web browser and go to `http://localhost:8000/admin/`. Log in with the superuser credentials you just created.


## Using the API

The project provides the following endpoints:

- auth/users/ - endpoint for creating a new user.
- auth/users/me/ - endpoint for getting information about the current user.
- auth/token/login/ - endpoint for getting an authentication token.
- auth/token/logout/ - endpoint for logging out.

To use these endpoints, follow these steps:

1. Create a new user by sending a POST request to the `auth/users/` endpoint. In the request body, include the following data:

```
{
    "username": "your_username",
    "password": "your_password"
}
```


2. Get an authentication token by sending a POST request to the `auth/token/login/` endpoint. In the request body, include the following data:

```
{
    "username": "your_username",
    "password": "your_password"
}
```


3. Use the token to access protected endpoints. To do this, add an `Authorization` header with the value `Token your_token` to each request.
For example:

    `curl -H "Authorization: Token <your-token>" http://localhost:8000/auth/users/me/`

4. Get information about the current user by sending a GET request to the `auth/users/me/` endpoint with the user's token in the Authorization header like in the example above.

5. Delete a user's token by sending a POST request to the `auth/token/logout/` endpoint with the user's token in the Authorization header.


## Database administration

To administer the database, you can use pgAdmin, which runs in a separate container. To access pgAdmin, follow these steps:

1. Open a browser and go to `http://localhost:5050/`.
2. Enter the login and password from your `.env` file to log in to pgAdmin.
3. Create a new connection to the necessary database
4. Connect to the database and perform the necessary operations.


## HOW run test
After start server, put next command in console:

`docker exec -it iteen.webapp bash run-test.sh`

If you got in logs "OK" and "TEST PASS! CONGRATULATION!!!", then tests were passed.
