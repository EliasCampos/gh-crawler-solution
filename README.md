# GitHub crawler

### Usage with virtual environment

#### Prerequisites
- Python 3

#### Configuring the virtual environment
Create a virtual environment:
```bash
python3 -m venv venv
```

Activate the virtual environment:
```bash
source venv/bin/activate
```

Install the required packages:
```bash
pip install -r requirements.txt
```

#### Installing the crawler
Install the crawler to be able to run it from the command line:
```bash
pip install -e .
```

#### Running the crawler
To run the crawler, execute the following command:
```bash
github_crawler example/config.json
```
Replace `example/config.json` with the path to the actual configuration file.
The configuration file should be a JSON file with the following structure:
```json
{
  "keywords": [
    "openstack",
    "nova",
    "css"
  ],
  "proxies": [
    "194.126.37.94:8080",
    "13.78.125.167:8080"
  ],
  "type": "Repositories"
}
```
The available values for the `"type"` parameter are:
- `"Repositories"`
- `"Issues"`
- `"Wikis`

#### Running the test
To run all the test, execute the following command:
```bash
pytest
```

To run tests and see a coverage report, execute the following command:
```bash
pytest --cov-report term --cov .
```
