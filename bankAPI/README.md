# BankAPI

## Tasks

- Implement assignment using:
  - Language: **Python**
  - Framework: **Flask**
- There should be API routes that allow them to:
  - Create a new bank account for a customer, with an initial deposit amount. A
    single customer may have multiple bank accounts.
  - Transfer amounts between any two accounts, including those owned by
    different customers.
  - Retrieve balances for a given account.
  - Retrieve transfer history for a given account.
- Write tests for your business logic

### How to Run

1. Clone the repo
2. install all requirements using pip
```pip install -r requirements.txt```
3. start app
``` ./startapp.sh ```

### How to Run the tests

To run the tests, user will have to change directory into the tests folder
and execute

- ``` python test_main_routes.py ```

### To build the docker Image

User should execute the following code

- ``` bash make-image.sh ```

### To access the API Documentation

Run ``` flask run ``` from the root folder `name...`
Or run ``` ./startapp.sh ``` from the root folder

open browser and navigate to
``` http://localhost:5000/ ```
