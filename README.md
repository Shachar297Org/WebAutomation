## Setup
1. Install [Python](https://www.python.org/downloads/) > 3.8
2. Install [Pipenv](https://pypi.org/project/pipenv/):
   
   **pip install --user pipenv**
3. Create a virtual environment from Pipfile and install packages:
   
   **pipenv install**
   
### Configure IDE (for local runs):
1. Configure Pytest as the default test runner in your IDE
2. Select Pipenv as the project interpreter

## Run the tests
```
 pytest <tests path> --allure-link-pattern'=issue:https://lumenisx.atlassian.net/browse/{}'
```

### Examples 
```
 pytest test --allure-link-pattern'=issue:https://lumenisx.atlassian.net/browse/{}' - running all tests
 pytest test/users --allure-link-pattern'=issue:https://lumenisx.atlassian.net/browse/{}' - running all tests in the users package
```
####TODO Add more examples 

### Allure HTML report
To see the actual report after your tests have finished, you need to use [Allure commandline utility](https://docs.qameta.io/allure/#_installing_a_commandline)
to generate report from the results.

```
 allure serve .allure_results
```
This command will show you generated report in your default browser.