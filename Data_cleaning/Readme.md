# Flask Case Management App

This Flask application provides a simple case management system that allows you to retrieve case information and add new cases. It includes two GET endpoints for retrieving case details and one POST endpoint for adding new cases.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [API Endpoints](#endpoints)
  - [Retrieve Case Text](#retrieve-case-text)
  - [Retrieve Case Laws](#retrieve-case-laws)
  - [Add New Case](#add-new-case)
- [Usage](#usage)
- [Error Handling](#Error-Handling)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed.
- Flask installed.
- SQLAlchemy installed.
- spaCy installed and the English language model.
- MySQL or another compatible database server running locally or with the appropriate connection details.

## Getting Started

1. Clone this repository to your local machine.
```bash
git clone https://github.com/your-username/flask-case-management-app.git
cd flask-case-management-app 
```


2. Edit the database connection details in the Flask app (`app.py`) to match your local MySQL database.

3. Run the Flask app.
```bash
python main.py

```

The app should now be running at `http://localhost:5000`.

## Endpoints

### Retrieve Case Text and Laws

#### GET `/CaseId/text`

This endpoint allows you to retrieve the clean text of a case by providing the `CaseId` as a parameter.

- **Method**: GET
- **Parameters**: `CaseId` (integer)
##### Example Usage

```bash
{
  http://localhost:5000/1/text
}
```

##### Example Response

```bash
{
  "CaseId": 1,
  "CleanText": "This is the clean text of case 1."
}
```

#### GET `/CaseId/laws`

This endpoint allows you to retrieve the clean text of a case by providing the `CaseId` as a parameter.

- **Method**: GET
- **Parameters**: `CaseId` (integer)
##### Example Usage

```bash
{
  http://localhost:5000/1/laws
}
```

##### Example Response

```bash
{
  "CaseId": 1,
  "Laws": "Law A, Law B, Law C"
}

```
### Add New Case

POST /addcase
This endpoint allows you to add a new case to the database by providing a JSON payload with the case details.

- Method: POST
- Request Payload (JSON):
-  Id (integer): The unique identifier of the case.
-  Judgement (string): The text of the case judgment.


##### Example Request

```bash
{
  curl -X POST -H "Content-Type: application/json" -d '{"Id": 2, "Judgement": "This is a new case judgment."}' http://localhost:5000/addcase
}

```
##### Example Responce
```bash
{
  "message": "Case added successfully"
}

```

### Usage

- Use the /CaseId/text endpoint to retrieve the clean text of a case.
- Use the /CaseId/laws endpoint to retrieve the laws associated with a case.
- Use the /addcase endpoint to add new cases to the system.

### Error and Exception Handling

In case of errors, the API will respond with appropriate HTTP status codes and error messages. Refer to the respective endpoint descriptions for details on error responses.

##### For Get requests

```bash
{
  200 : Case data fetched Successfully
  404 : Case data not found
}

```

##### For Post requests

```bash
{
  201 : Case data added Successfully
  400 : Invalid data provided 
  500 : Exception Occurred
}

```