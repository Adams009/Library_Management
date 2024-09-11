# API Overview

**Base URL:** `/users`

This API provides endpoints to manage user data, including creating, retrieving, updating, and deleting user records.

## Endpoints

### 1. Register a New User

- **Route:** `api/register`
- **Method:** POST
- **Description:** Registers a new user in the system.
- **Required Data:**
  ```json
  {
    "username": "string",
    "password": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "phone_number": "string",
    "date_of_birth": "string",
    "address": "string",
    "guarantor_fullname": "string",
    "guarantor_phone_number": "string",
    "guarantor_address": "string",
    "guarantor_relationship": "string"
  }

    Returns:
        Success: JSON object with user's ID and details (HTTP 201 Created)
        Error: JSON object with error message (e.g., missing fields, username/email already exists) (HTTP 400 Bad Request)

    Example Request:

    json

    {
      "username": "john_doe",
      "password": "secureP@ssw0rd",
      "email": "john.doe@google.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "+2348156789009",
      "date_of_birth": "1990-01-01",
      "address": "123 Elm Street, Springfield, IL",
      "guarantor_fullname": "Jane Doe",
      "guarantor_phone_number": "+2349087654321",
      "guarantor_address": "456 Oak Avenue, Springfield, IL",
      "guarantor_relationship": "Spouse"
    }

2. ### Get a User by ID

   - **Route:** `api/users/<int:id>`
   - **Method:** GET
   - **Description:** Retrieves a user by their ID from the database.
   - **Arguments:**
        `id: User ID (integer)`
   - **Returns:**
        `Success: JSON object containing the user's details (HTTP 200 OK)`
        `Error: JSON object with error message if user not found (HTTP 404 Not Found)`

3. ### Get All Users or Filtered Users

   - **Route:** `api/users`
   - **Method:** GET
   - **Description:** Retrieves all users or users based on optional filters.
   - **Optional Parameters:**
        `page: Page number for pagination (default: 1)`
        `per_page: Number of users per page (default: 10)`
        `username: Filter users by username (string, optional)`
        `email: Filter users by email (string, optional)`
   - **Returns:**
        `Success: JSON object containing a list of users and pagination information (HTTP 200 OK)`
        `Error: JSON object with error message if no users are found for the provided filters or general case (HTTP 404 Not Found)`

4. ### Update a User by ID

   - **Route:** `api/users/<int:id>`
   - **Method:** PUT
   - **Description:** Updates an existing user by their ID with the provided data.
   - **Arguments:**
        `id: User ID (integer)`
   - **Optional Parameters:**
        `username, password, email, first_name, last_name, phone_number, address, guarantor_fullname, guarantor_phone_number, guarantor_address, guarantor_relationship: Fields to be updated (strings, optional)`
   - **Returns:**
        `Success: JSON object with updated user details and a success message (HTTP 200 OK)`
        `Error: JSON object with error message if user not found or if validation fails (HTTP 400 Bad Request or HTTP 404 Not Found)`

5. ### Delete a User by ID

   - **Route:** `api/users/<int:id>`
   - **Method:** DELETE
   - **Description:** Deletes a user from the database by their ID.
   - **Arguments:**
        `id: User ID (integer)`
   - **Returns:**
        `Success: JSON object with a success message (HTTP 200 OK)`
        `Error: JSON object with error message if user not found (HTTP 404 Not Found)`

### Error Handling

    400 Bad Request: Returned for invalid input, missing required data, or validation issues.
    404 Not Found: Returned when a user is not found based on ID or when no users match the provided filters.

### Notes

    Ensure to provide data in JSON format for POST and PUT requests.
