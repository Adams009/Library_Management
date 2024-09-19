# API Documentation
## Endpoints
                           ROUTES FOR USERS
### 1. Register a New User

- **Route:** `/api/register`
- **Method:** `POST`
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
  ```
     - **Returns:**
        - `Success`: JSON object with user's ID and details.
            - HTTP Status Code: 201 Created
        - `Error`: JSON object with error message (e.g., missing fields, username/email already exists).
            - HTTP Status Code: 400 Bad Request

    Example Request:
```bash
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
```
- **Error Responses:**
  - `400 Bad Request`:
```bash
json

{
  "error": "username already exists"
}
```
### 2. Get a User by ID

- **Route:** `/api/users/<int:id>`
- **Method:** `GET`
- **Description:** Retrieves a user by their ID from the database.
- **Arguments:**
  - `id`: User ID (integer)
- **Returns:**
  - `Success`: JSON object containing the user's details.
    - **HTTP Status Code:** 200 OK
  - `Error`: JSON object with error message if user not found.
    - **HTTP Status Code:** 404 Not Found

- **Example Request:**

  ```bash
  GET /api/users/1

    Example Response:

    json

  {
    "user_id": 1,
    "phone_number": "+2348156789009",
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@google.com"
  }

- **Error Responses:**
    - `404 Not Found`:
  ```bash
      json

  {
    "error": "User not found"
  }
  ```
### 3. Retrieve All Users or By Filter

- **Route:** `/api/users`
- **Method:** `GET`
- **Description:** Retrieves a list of users from the database, with optional filtering by username or email, and pagination.
- **Query Parameters:**
  - `page` (integer, optional): The page number to retrieve (default: 1).
  - `per_page` (integer, optional): The number of users per page (default: 10).
  - `username` (string, optional): Filter users by username.
  - `email` (string, optional): Filter users by email address.

- **Returns:**
    - **Success:** JSON object containing a list of users, pagination details, and the total number of results.
        - HTTP Status Code: 200 OK
    - **Error:** JSON object with error message if pagination parameters are invalid.
        - HTTP Status Code: 400 Bad Request

- **Example Request:**
  ```bash
  curl -X GET "http://yourapiurl/api/users?page=1&per_page=10"

    Success Response:

    json

  {
    "users": [
      {
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@google.com"
      },
      ...
    ],
    "total_pages": 5,
    "total_results": 50,
    "per_page": 10,
    "page": 1
  }

Error Responses:

    400 Bad Request:

  ```bash
    json

  {
    "error": "Page and per_page parameters must be positive integers"
  }
  ```
### 4. Update a User by ID

- **Route:** `/api/users/<id>`
- **Method:** `PUT`
- **Description:** Update a user’s details by their ID and return the updated user object if successful; otherwise, return an error message.
- **Path Parameters:**
  - `id` (integer): The unique identifier of the user to update.
- **Required Data:**

  ```json
  {
    "username": "string",
    "password": "string",
    "old_password": "string",
    "new_password": "string",
    "email": "string",
    "first_name": "string",
    "last_name": "string",
    "phone_number": "string",
    "address": "string",
    "guarantor_fullname": "string",
    "guarantor_phone_number": "string",
    "guarantor_address": "string",
    "guarantor_relationship": "string"
  }

    Returns:
        Success: JSON object containing the updated user details.
            HTTP Status Code: 200 OK
        Error: JSON object with error message if there are issues with the update (e.g., invalid data, user not found, or unique constraints).
            HTTP Status Code: 400 Bad Request
            HTTP Status Code: 404 Not Found
            HTTP Status Code: 409 Conflict
            HTTP Status Code: 500 Internal Server Error

    Example Request:

  ```
  ```bash
  curl -X PUT "http://yourapiurl/api/users/1" -H "Content-Type: application/json" -d '{
    "username": "john_doe_updated",
    "old_password": "secureP@ssw0rd",
    "new_password": "newSecureP@ssw0rd",
    "email": "john.doe.updated@google.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+2348156789000",
    "address": "123 Elm Street, Springfield, IL",
    "guarantor_fullname": "Jane Doe",
    "guarantor_phone_number": "+2349087654320",
    "guarantor_address": "456 Oak Avenue, Springfield, IL",
    "guarantor_relationship": "Spouse"
  }'
  ```
Error Responses:
  ```bash
    400 Bad Request:

  
    json

  {
    "error": "Invalid or missing data"
  }
  ```
  ```bash
  404 Not Found:

  json

  {
    "error": "User not found"
  }
  ```
  ```bash
  409 Conflict:

  json

  {
    "error": "Username already exists"
  }
  ```
  ```bash
  500 Internal Server Error:

  json

  {
    "error": "An error occurred while updating the user: [error message]"
  }
  ```
### 5. Delete a User by ID

- **Route:** `/api/users/<id>`
- **Method:** `DELETE`
- **Description:** Deletes a user identified by their ID from the database. If the user is found, the user will be removed, and a successful response will be returned. If the user does not exist, a 404 error will be returned. If an error occurs during deletion, an error message will be returned.
- **Path Parameters:**
  - `id` (integer): The unique identifier of the user to delete.
- **Returns:**
    - **Success:** JSON object indicating successful deletion with the user’s ID and username.
        - HTTP Status Code: 200 OK
    - **Error:** JSON object with error message if the user is not found or if an error occurs during deletion.
        - HTTP Status Code: 404 Not Found
        - HTTP Status Code: 500 Internal Server Error

- **Example Request:**
  ```bash
  curl -X DELETE "http://yourapiurl/api/users/1"

    Success Response:

  ```
  ```bash
    json

  {
    "message": "User deleted successfully",
    "user_id": 1,
    "username": "john_doe"
  }
  ```
Error Responses:

    404 Not Found:

  ```bash
    json

  {
    "error": "User not found"
  }
  ```
    500 Internal Server Error:
  ```bash
  json

  {
    "error": "An error occurred while deleting the user: [error message]"
  }
  ```

### 6. Catch-All Route

- **Route:** `/<path:path>`
- **Method:** `GET, POST, PUT, DELETE`
- **Description:** Handles all unmatched routes and returns a 404 error message. This endpoint responds to any HTTP methods (GET, POST, PUT, DELETE) for any path that is not explicitly defined in the blueprint. It will return a 404 error with a message indicating that the requested URL was not found on the server.
- **Returns:**
    - **Error:** JSON object with an error message indicating that the requested URL was not found.
        - HTTP Status Code: 404 Not Found

- **Example Request:**
  ```bash
  curl -X GET "http://api/books/unknown_route"

    Error Response:

    json

  {
    "error": "The requested URL was not found on the server. Please check your spelling and try again."
  }
  ```
                        ROUTES FOR BOOKS

### 1. Retrieve a List of Books

- **Route:** `/api/books`
- **Method:** `GET`
- **Description:** Retrieves a list of books from the database with optional filtering and pagination. Returns a paginated list of books in JSON format.

- **Optional Query Parameters:**
  - `page`: The page number of the books to be returned (default is 1).
  - `per_page`: The number of books per page to be returned (default is 10).
  - `title`: The title of the book to be returned.
  - `author`: The author of the book to be returned.
  - `year`: The year of publication of the book to be returned.
  - `isbn`: The ISBN of the book to be returned.
  - `available`: Whether the book is available for borrowing (`true`/`false`).
  - `language`: The language of the book to be returned.
  - `category`: The category of the book to be returned.
  - `publisher`: The publisher of the book to be returned.

- **Returns:**
  - `Success`: JSON object containing a paginated list of books.
    - **HTTP Status Code:** 200 OK
    - **Example Response:**
      ```json
      {
        "total_result": 100,
        "page": 1,
        "per_page": 10,
        "books": [
          {
            "id": 1,
            "title": "Example Book",
            "author": "John Doe",
            "year": 2021,
            "isbn": "1234567890",
            "available": true,
            "language": "English",
            "category": "Fiction",
            "publisher": "Example Publisher"
          }
          // More books here
        ],
        "total_pages": 10
      }
      ```

  - `Error`: JSON object with an error message if parameters are invalid or no books are found.
    - **HTTP Status Code:** 400 Bad Request
    - **Example Error Response:**
      ```json
      {
        "error": "Page and per_page parameters must be positive integers"
      }
      ```

    - **HTTP Status Code:** 200 OK (when no books match the provided criteria)
    - **Example Error Response:**
      ```json
      {
        "message": "No books found matching the given criteria"
      }
      ```

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/api/books?page=2&per_page=5&author=John%20Doe"  


  ```
### 2. Retrieve a Specific Book

- **Route:** `/api/books/<int:book_id>`
- **Method:** `GET`
- **Description:** Retrieves a specific book by its ID from the database and returns its details in JSON format.

- **Required Path Parameter:**
  - `book_id` (int): The ID of the book to retrieve.

- **Returns:**
  - `Success`: JSON object containing the book's details.
    - **HTTP Status Code:** 200 OK
    - **Example Response:**
      ```json
      {
        "id": 1,
        "title": "Example Book",
        "author": "John Doe",
        "year": 2021,
        "isbn": "1234567890",
        "available": true,
        "language": "English",
        "category": "Fiction",
        "publisher": "Example Publisher"
      }
      ```

  - `Error`: JSON object with an error message if the book is not found.
    - **HTTP Status Code:** 404 Not Found
    - **Example Error Response:**
      ```json
      {
        "error": "Book not found"
      }
      ```

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/api/books/1"

  ```

### 3. Add a New Book

- **Route:** `/api/books`
- **Method:** `POST`
- **Description:** Adds a new book to the database and returns the book's details in JSON format if successful. 

- **Request Body:**
  - **JSON Body:**
    - `title` (str): The title of the book.
    - `author` (str): The author of the book.
    - `year` (int): The publication year of the book.
    - `isbn` (str): The ISBN of the book.
    - `available_copies` (int): The number of available copies of the book.
    - `total_copies` (int): The total number of copies of the book.
    - `language` (str): The language of the book.
    - `category` (str): The category of the book.
    - `publisher` (str): The publisher of the book.
    - `cover_image_url` (str, optional): The URL of the book's cover image.

- **HTTP Response Codes:**
  - `201 Created`: If the book is successfully added, returns the book's details.
    - **Example Response:**
      ```json
      {
        "id": 1,
        "title": "Example Book",
        "author": "John Doe",
        "year": 2021,
        "isbn": "1234567890",
        "available": true,
        "available_copies": 5,
        "total_copies": 10,
        "language": "English",
        "category": "Fiction",
        "publisher": "Example Publisher",
        "cover_image_url": "http://example.com/image.jpg",
        "a_message": "Book added successfully"
      }
      ```
  - `400 Bad Request`: If the request is missing required fields or contains invalid data.
    - **Example Error Response:**
      ```json
      {
        "error": "Missing required field: title"
      }
      ```
  - `409 Conflict`: If a book with the same ISBN already exists in the database.
    - **Example Error Response:**
      ```json
      {
        "error": "Book already exists"
      }
      ```
  - `500 Internal Server Error`: If there is an unexpected error during the book addition process.
    - **Example Error Response:**
      ```json
      {
        "error": "An unexpected error occurred",
        "message": "Detailed error message here"
      }
      ```

- **Example Request:**
  ```bash
  curl -X POST "http://example.com/api/books" -H "Content-Type: application/json" -d '{
    "title": "New Book",
    "author": "Jane Smith",
    "year": 2024,
    "isbn": "0987654321",
    "available_copies": 3,
    "total_copies": 5,
    "language": "English",
    "category": "Non-Fiction",
    "publisher": "New Publisher",
    "cover_image_url": "http://example.com/new-image.jpg"
  }'
  ```

### 4. Update an Existing Book

- **Route:** `/api/books/<int:book_id>`
- **Method:** `PUT`
- **Description:** Updates the details of an existing book in the database and returns the updated book details in JSON format if successful.

- **Request Body (JSON):**
  - **Optional Fields:**
    - `title` (str): The new title of the book.
    - `author` (str): The new author of the book.
    - `year` (int): The new publication year of the book.
    - `isbn` (str): The new ISBN of the book.
    - `available` (bool): The new availability status of the book (`true`/`false`).
    - `available_copies` (int): The new number of available copies of the book.
    - `total_copies` (int): The new total number of copies of the book.
    - `language` (str): The new language of the book.
    - `category` (str): The new category of the book.
    - `publisher` (str): The new publisher of the book.
    - `cover_image_url` (str): The new URL of the book's cover image.

- **Args:**
  - `book_id` (int): The ID of the book to update.

- **HTTP Response Codes:**
  - `200 OK`: If the book is successfully updated.
    - **Example Response:**
      ```json
      {
        "a_message": "Details updated successfully",
        "updated_fields": {
          "title": "Updated Book Title",
          "author": "Updated Author"
        }
      }
      ```
  - `400 Bad Request`: If the request contains invalid data or logical errors (e.g., available copies exceed total copies).
    - **Example Error Response:**
      ```json
      {
        "error": "Total copies must be greater than or equal to available copies"
      }
      ```
  - `404 Not Found`: If the book with the specified ID is not found.
    - **Example Error Response:**
      ```json
      {
        "error": "Book not found"
      }
      ```
  - `409 Conflict`: If no changes are made because the new values are the same as the current values.
    - **Example Error Response:**
      ```json
      {
        "error": "New Book title is the same as the current book title"
      }
      ```
  - `500 Internal Server Error`: If there is an unexpected error during the update process.
    - **Example Error Response:**
      ```json
      {
        "error": "An unexpected error occurred",
        "message": "Detailed error message here"
      }
      ```

- **Example Request:**
  ```bash
  curl -X PUT "http://example.com/api/books/1" -H "Content-Type: application/json" -d '{
    "title": "Updated Book Title",
    "author": "Updated Author",
    "year": 2024,
    "isbn": "0987654321",
    "available": true,
    "available_copies": 3,
    "total_copies": 5,
    "language": "English",
    "category": "Updated Category",
    "publisher": "Updated Publisher",
    "cover_image_url": "http://example.com/updated-image.jpg"
  }'
  ```

### 5. Delete a Book

- **Route:** `/api/books/<int:book_id>`
- **Method:** `DELETE`
- **Description:** Deletes a book from the database by its ID and returns a confirmation message if successful.

- **Args:**
  - `book_id` (int): The ID of the book to delete.

- **HTTP Response Codes:**
  - `200 OK`: If the book is successfully deleted.
    - **Example Response:**
      ```json
      {
        "book_id": 1,
        "title": "Book Title",
        "author": "Book Author",
        "a_message": "Book deleted successfully"
      }
      ```
  - `404 Not Found`: If the book with the specified ID is not found.
    - **Example Error Response:**
      ```json
      {
        "error": "Book not found"
      }
      ```
  - `500 Internal Server Error`: If there is an unexpected error during the deletion process.
    - **Example Error Response:**
      ```json
      {
        "error": "An unexpected error occurred",
        "message": "Detailed error message here"
      }
      ```

- **Example Request:**
  ```bash
  curl -X DELETE "http://example.com/api/books/1"
  ```

### 6. Check Book Availability

- **Route:** `/api/books/<int:book_id>/availability`
- **Method:** `GET`
- **Description:** Checks the availability status of a book by its ID and returns the status in JSON format if successful.

- **Args:**
  - `book_id` (int): The ID of the book to check availability.

- **HTTP Response Codes:**
  - `200 OK`: If the book is found and availability status is successfully retrieved.
    - **Example Response:**
      ```json
      {
        "id": 1,
        "title": "Book Title",
        "available": true,
        "author": "Book Author",
        "year": 2021,
        "isbn": "1234567890"
      }
      ```
  - `404 Not Found`: If the book with the specified ID is not found.
    - **Example Error Response:**
      ```json
      {
        "error": "Book not found."
      }
      ```

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/api/books/1/availability"
  ```

### 7. Retrieve All Books Availability

- **Route:** `/api/books/availability`
- **Method:** `GET`
- **Description:** Retrieve the availability status of all books or filter by specific criteria and return it in JSON format.

- **Optional Query Parameters:**
  - `page` (int): The page number to return (default is 1).
  - `per_page` (int): The number of books per page (default is 10).
  - `title` (str): Filter books by title.
  - `author` (str): Filter books by author.
  - `year` (int): Filter books by publication year.
  - `isbn` (str): Filter books by ISBN.
  - `available` (bool): Filter books by availability (true/false).
  - `language` (str): Filter books by language.
  - `category` (str): Filter books by category.
  - `publisher` (str): Filter books by publisher.

- **HTTP Response Codes:**
  - `200 OK`: If books are found and availability status is successfully retrieved.
    - **Example Response:**
      ```json
      {
        "total_items": 50,
        "page": 1,
        "per_page": 10,
        "total_pages": 5,
        "books": [
          {
            "id": 1,
            "title": "Book Title",
            "available": true,
            "author": "Book Author",
            "year": 2021,
            "isbn": "1234567890"
          },
          ...
        ]
      }
      ```
  - `400 Bad Request`: If query parameters are invalid.
    - **Example Error Response:**
      ```json
      {
        "error": "Page and per_page parameters must be positive integers"
      }
      ```

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/api/books/availability?page=1&per_page=10&title=Book Title"
  ```

### 8. Catch-All Route

- **Route:** `/api/<path:path>`
- **Method:** `GET`, `POST`, `PUT`, `DELETE`
- **Description:** Handles all unmatched routes and returns a 404 error message.

- **Args:**
  - `path` (str): The unmatched path part of the URL that was requested.

- **HTTP Response Codes:**
  - `404 Not Found`: If the requested URL does not match any defined routes within the `books_bp` blueprint.
    - **Example Error Response:**
      ```json
      {
        "error": "The requested URL was not found on the server. Please check your spelling and try again."
      }
      ```

- **Example Request:**
  ```bash
  curl -X GET "http://api/books/nonexistent/path"
  ```

                          ROUTES FOR BORROW

### 1. Borrow a Book

- **Route:** `/books/<int:book_id>/borrow`
- **Method:** `POST`
- **Description:** Creates a new borrow record for a specific book by its ID. The endpoint expects a JSON request body containing borrower details such as `user_id`, `username`, and `email`. Several validations are performed, including checking if the book is available and if the borrower’s details are correct.

- **Request Body (JSON):**
  - `user_id` (int): The ID of the user borrowing the book.
  - `username` (string): The username of the user borrowing the book.
  - `email` (string): The email address of the user borrowing the book.

- **Args:**
  - `book_id` (int): The ID of the book to borrow.

- **HTTP Response Codes:**
  - **201 Created:** If the book is successfully borrowed and the borrow record is created.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "id": 1,
        "book_id": 123,
        "user_id": 456,
        "borrow_date": "2024-09-13",
        "due_date": "2024-10-13",
        "returned_date": null
      }
      ```
  - **400 Bad Request:** If the request body is missing required fields, or if the `user_id`, `username`, or `email` are invalid.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "Invalid user_id: user_id must be an integer and greater than 0"
      }
      ```
  - **404 Not Found:** If the book or the borrower cannot be found.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "Book not found"
      }
      ```
  - **409 Conflict:** If the book is not available or if the user has already borrowed the book without returning it.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "Book is not available"
      }
      ```
  - **500 Internal Server Error:** For any unexpected errors during the borrowing process.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "An unexpected error occurred"
      }
      ```

- **Returns:**
  - JSON: The borrow record in JSON format if borrowing is successful. Includes details such as `book_id`, `user_id`, `borrow_date`, `due_date`, and `returned_date`.

- **Example Request:**
  ```bash
  curl -X POST "http://example.com/books/123/borrow" \
       -H "Content-Type: application/json" \
       -d '{
             "user_id": 456,
             "username": "john_doe",
             "email": "john.doe@example.com"
           }'

    Example Response (Success):

  ```bash
      json

    {
      "id": 1,
      "book_id": 123,
      "user_id": 456,
      "borrow_date": "2024-09-13",
      "due_date": "2024-10-13",
      "returned_date": null
    }
  ```
Example Response (Error):

  ```bash  
    json

  {
    "error": "username is required" 
  }
  ```
### 2. Retrieve Borrowed Books

- **Route:** `/borrow`
- **Method:** `GET`
- **Description:** Retrieves a list of all borrowed books or a specific borrowed book based on provided parameters and returns it in JSON format.

- **Optional Query Parameters:**
  - `page` (int): The page number of the results to return (default is 1).
  - `per_page` (int): The number of borrowed books per page (default is 10).
  - `user_id` (int): Filter borrowed books by user ID.
  - `book_id` (int): Filter borrowed books by book ID.
  - `borrow_date` (string): Filter borrowed books by borrow date (format: YYYY-MM-DD).
  - `due_date` (string): Filter borrowed books by due date (format: YYYY-MM-DD).
  - `returned_date` (string): Filter borrowed books by returned date (format: YYYY-MM-DD).
  - `title` (string): Filter borrowed books by book title.
  - `author` (string): Filter borrowed books by book author.
  - `category` (string): Filter borrowed books by book category.
  - `publisher` (string): Filter borrowed books by book publisher.
  - `language` (string): Filter borrowed books by book language.

- **HTTP Response Codes:**
  - **200 OK:** If borrowed books are found and returned successfully.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "borrowed_books": [
          {
            "id": 1,
            "book_id": 123,
            "user_id": 456,
            "borrow_date": "2024-01-15",
            "due_date": "2024-02-15",
            "returned_date": null,
            "title": "Example Book Title",
            "author": "Jane Doe",
            "year": 2022,
            "isbn": "9876543210",
            "language": "English",
            "category": "Fiction",
            "publisher": "Example Publisher",
            "available": true,
            "cover_image_url": "http://example.com/image.jpg"
          }
          // More borrowed books here
        ],
        "total_result": 25,
        "page": 1,
        "per_page": 10,
        "total_pages": 3
      }
      ```

  - **400 Bad Request:** If any of the parameters are invalid or incorrectly formatted.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "Invalid borrow_date: borrow_date must be in YYYY-MM-DD format"
      }
      ```

  - **404 Not Found:** If no borrowed books match the specified criteria.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "No borrowed books found matching the specified criteria"
      }
      ```

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/borrow?page=2&per_page=5&author=Jane%20Doe"
  ```

### 3. Retrieve Specific Borrowed Book

- **Route:** `</borrow/<int:book_id>`
- **Method:** `GET`
- **Description:** Retrieve information about a specific borrowed book based on the provided book ID. This endpoint can also filter the results based on additional query parameters such as user ID, borrow date, due date, and return date. The response is returned in JSON format and includes details about the borrowed book.

- **Optional Query Parameters:**
  - `page` (int): The page number of results to return (default is 1).
  - `per_page` (int): The number of borrowed book records per page (default is 10).
  - `user_id` (int): Filter borrowed books by user ID.
  - `borrow_date` (string): Filter borrowed books by borrow date (format: YYYY-MM-DD).
  - `due_date` (string): Filter borrowed books by due date (format: YYYY-MM-DD).
  - `return_date` (string): Filter borrowed books by return date (format: YYYY-MM-DD).

- **Args:**
  - `book_id` (int): The unique identifier for the book.

- **HTTP Response Codes:**
  - **200 OK:** If borrowed books are found and returned successfully.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "borrowed_books": [
          {
            "id": 1,
            "book_id": 123,
            "user_id": 456,
            "borrow_date": "2024-01-15",
            "due_date": "2024-02-15",
            "returned_date": null,
            "title": "Example Book Title",
            "author": "Jane Doe",
            "year": 2022,
            "isbn": "9876543210",
            "language": "English",
            "category": "Fiction",
            "publisher": "Example Publisher",
            "available": true,
            "cover_image_url": "http://example.com/image.jpg"
          }
          // More borrowed books here
        ],
        "total_result": 5,
        "page": 1,
        "per_page": 10,
        "total_pages": 1
      }
      ```

  - **400 Bad Request:** If any of the parameters are invalid or incorrectly formatted.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "Invalid borrow_date: borrow_date must be in YYYY-MM-DD format"
      }
      ```

  - **404 Not Found:** If no borrowed books matching the specified criteria are found.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "No borrowed books found matching the specified criteria"
      }
      ```

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/borrow/123?page=1&per_page=10&user_id=456"
  ```

### 4. Retrieve Unreturned Borrowed Books

- **Route:** `/unreturned`
- **Method:** `GET`
- **Description:** Retrieve all borrowed books that have not been returned yet. This endpoint supports filtering based on various optional query parameters such as title, author, category, publisher, language, user ID, book ID, borrow date, and due date. The results are returned in a paginated JSON format.

- **Optional Query Parameters:**
  - `page` (int): The page number of results to retrieve (default is 1).
  - `per_page` (int): The number of borrowed book records per page (default is 10).
  - `title` (string): Filter unreturned books by title.
  - `author` (string): Filter unreturned books by author.
  - `category` (string): Filter unreturned books by category.
  - `publisher` (string): Filter unreturned books by publisher.
  - `language` (string): Filter unreturned books by language.
  - `user_id` (int): Filter unreturned books by user ID.
  - `book_id` (int): Filter unreturned books by book ID.
  - `borrow_date` (string): Filter unreturned books by borrow date (format: YYYY-MM-DD).
  - `due_date` (string): Filter unreturned books by due date (format: YYYY-MM-DD).

- **HTTP Response Codes:**
  - **200 OK:** If unreturned borrowed books are found and returned successfully.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "borrowed_books": [
          {
            "id": 1,
            "book_id": 123,
            "user_id": 456,
            "borrow_date": "2024-01-15",
            "due_date": "2024-02-15",
            "returned_date": null,
            "title": "Example Book Title",
            "author": "Jane Doe",
            "year": 2022,
            "isbn": "9876543210",
            "language": "English",
            "category": "Fiction",
            "publisher": "Example Publisher",
            "available": true,
            "cover_image_url": "http://example.com/image.jpg"
          }
          // More unreturned books here
        ],
        "total_result": 5,
        "page": 1,
        "per_page": 10,
        "total_pages": 1
      }
      ```

  - **400 Bad Request:** If any of the parameters are invalid or incorrectly formatted.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "Invalid borrow_date: borrow_date must be in YYYY-MM-DD format"
      }
      ```

  - **404 Not Found:** If no unreturned borrowed books matching the specified criteria are found.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "No unreturned borrowed books found matching the specified criteria"
      }
      ```

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/unreturned?page=1&per_page=10&author=Jane%20Doe"
  ```

### 5. Catch-All Route

- **Route:** `/<path:path>`
- **Method:** `GET`, `POST`, `PUT`, `DELETE`
- **Description:** Handles all unmatched routes within the `borrow_bp` blueprint and returns a 404 error message. This endpoint serves as a fallback for any requests that do not match the explicitly defined routes within the blueprint. It is invoked for any HTTP method and any path that is not explicitly defined.

- **Args:**
  - `path` (string): The unmatched path part of the URL that was requested.

- **HTTP Response Codes:**
  - **404 Not Found:** Returned when the requested URL does not match any defined route in the blueprint.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "The requested URL was not found on the server. Please check your spelling and try again."
      }
      ```

- **Returns:**
  - JSON: A JSON object containing an error message indicating that the requested URL was not found on the server. It suggests checking the spelling and trying again.

- **Example Request:**
  ```bash
  curl -X GET "http://api/borrow/nonexistent/path"
  ```

                              RETURN ROUTES

### 1. Return a Borrowed Book

- **Route:** `/books/<int:book_id>/return`
- **Method:** `POST`
- **Description:** Processes the return of a borrowed book for a specific user. It updates the borrow record and includes the return details such as user ID, username, email, and damage status. The endpoint performs several validations and checks to ensure the return is processed correctly.

- **Request Body (JSON):**
    - `user_id` (int): The ID of the user returning the book.
    - `username` (string): The username of the user returning the book.
    - `email` (string): The email address of the user returning the book.
    - `damage` (string): The damage status of the book, which should be "true" or "false".

- **Args:**
    - `book_id` (int): The ID of the book being returned.

- **HTTP Response Codes:**
    - **200 OK:** If the book is successfully returned and the borrow record is updated.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "a_message": "Book returned successfully",
            "id": 1,
            "user_id": 456,
            "book_id": 123,
            "borrow_date": "2024-01-15",
            "due_date": "2024-02-15",
            "returned_date": "2024-01-20",
            "book_title": "Example Book Title",
            "damage_status": "false",
            "damage_fine": 0,
            "fine_amount": 5,
            "total_fine": 5
          }
          ```

    - **400 Bad Request:** If the request body is missing required fields or contains invalid data.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "Invalid user_id: user_id must be an integer and greater than 0"
          }
          ```

    - **404 Not Found:** If the user or borrow record cannot be found.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "User not found: id, username, and/or email do not match"
          }
          ```

    - **409 Conflict:** If the book has already been returned or if the record was not found.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "Book already returned."
          }
          ```

    - **500 Internal Server Error:** For any unexpected errors during the return process.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "An unexpected error occurred",
            "message": "Detailed error message"
          }
          ```

- **Example Request:**
  ```bash
  curl -X POST "http://example.com/books/123/return" \
    -H "Content-Type: application/json" \
    -d '{
          "user_id": 456,
          "username": "johndoe",
          "email": "johndoe@example.com",
          "damage": "false"
        }'
  ```
### 2. Retrieve All Returned Books

- **Route:** `/return`
- **Method:** `GET`
- **Description:** Retrieves a paginated list of all returned books. This endpoint supports various optional filters to narrow down the results based on book and user details, as well as dates. It also handles pagination through query parameters.

- **Query Parameters:**
    - `page` (int): The page number for pagination. Defaults to 1.
    - `per_page` (int): The number of items per page. Defaults to 10.
    - `title` (string): Filter by book title (partial match).
    - `author` (string): Filter by book author (partial match).
    - `category` (string): Filter by book category (partial match).
    - `publisher` (string): Filter by book publisher (partial match).
    - `language` (string): Filter by book language (partial match).
    - `user_id` (int): Filter by the ID of the user who borrowed the book.
    - `book_id` (int): Filter by the ID of the book.
    - `borrow_date` (string): Filter by the borrow date (format: YYYY-MM-DD).
    - `due_date` (string): Filter by the due date (format: YYYY-MM-DD).
    - `return_date` (string): Filter by the return date (format: YYYY-MM-DD).

- **HTTP Response Codes:**
    - **200 OK:** If the request is successful and returned books are retrieved.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "returned_books": [
              {
                "id": 1,
                "user_id": 456,
                "book_id": 123,
                "borrow_date": "2024-01-15",
                "due_date": "2024-02-15",
                "returned_date": "2024-01-20",
                "book_title": "Example Book Title",
                "damage_status": "false",
                "damage_fine": 0,
                "fine_amount": 5,
                "total_fine": 5
              }
              // More returned books here
            ],
            "total_result": 5,
            "page": 1,
            "per_page": 10,
            "total_pages": 1
          }
          ```

    - **400 Bad Request:** If the query parameters are invalid or incorrectly formatted.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "Invalid borrow_date: borrow_date must be in YYYY-MM-DD format"
          }
          ```

    - **404 Not Found:** If no returned books matching the specified criteria are found.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "No Returned books found matching the specified criteria"
          }
          ```

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/return?page=1&per_page=10&author=Jane%20Doe"
  ```
### 3. Retrieve Specific Returned Book

- **Route:** `/return/<int:book_id>`
- **Method:** `GET`
- **Description:** Retrieves a paginated list of all returned instances for a specific book identified by its `book_id`. This endpoint supports optional filtering based on user ID and date ranges. It also supports pagination through query parameters.

- **Args:**
    - `book_id` (int): The ID of the book whose returned instances are to be retrieved.

- **Query Parameters:**
    - `page` (int): The page number for pagination. Defaults to 1.
    - `per_page` (int): The number of items per page. Defaults to 10.
    - `user_id` (int): Filter by the ID of the user who borrowed the book.
    - `borrow_date` (string): Filter by the borrow date (format: YYYY-MM-DD).
    - `due_date` (string): Filter by the due date (format: YYYY-MM-DD).
    - `return_date` (string): Filter by the return date (format: YYYY-MM-DD).

- **HTTP Response Codes:**
    - **200 OK:** If the request is successful and the returned book instances are retrieved.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "returned_books": [
              {
                "id": 1,
                "user_id": 456,
                "book_id": 123,
                "borrow_date": "2024-01-15",
                "due_date": "2024-02-15",
                "returned_date": "2024-01-20",
                "book_title": "Example Book Title",
                "damage_status": "false",
                "damage_fine": 0,
                "fine_amount": 5,
                "total_fine": 5
              }
              // More returned books here
            ],
            "total_result": 5,
            "page": 1,
            "per_page": 10,
            "total_pages": 1
          }
          ```

    - **400 Bad Request:** If the query parameters are invalid or incorrectly formatted.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "Invalid borrow_date: borrow_date must be in YYYY-MM-DD format"
          }
          ```

    - **404 Not Found:** If no returned instances matching the specified criteria are found.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "No Returned books found matching the specified criteria"
          }
          ```

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/return/123?page=1&per_page=10&user_id=456"
  ```
### 4. Catch-All Route

- **Route:** `/<path:path>`
- **Method:** `GET`, `POST`, `PUT`, `DELETE`
- **Description:** Handles all unmatched routes within the `borrow_bp` blueprint and returns a 404 error message. This endpoint serves as a fallback for any requests that do not match the explicitly defined routes within the blueprint. It is invoked for any HTTP method and any path that is not explicitly defined.

- **Args:**
  - `path` (string): The unmatched path part of the URL that was requested.

- **HTTP Response Codes:**
  - **404 Not Found:** Returned when the requested URL does not match any defined route in the blueprint.
    - **Content-Type:** application/json
    - **Response Body:**
      ```json
      {
        "error": "The requested URL was not found on the server. Please check your spelling and try again."
      }
      ```

- **Returns:**
  - JSON: A JSON object containing an error message indicating that the requested URL was not found on the server. It suggests checking the spelling and trying again.

- **Example Request:**
  ```bash
  curl -X GET "http://api/return/nonexistent/path"
  ```

  ```bash

                    READ-LIST ROUTES

### 1. Add a Book to a User's Reading List

- **Route:** `/users/<int:user_id>/read`
- **Method:** `POST`
- **Description:** Allows a user to add a book to their reading list. The request must contain a JSON body with the book ID, username, and email. The endpoint performs validations to ensure that the user exists, the book is valid, and that the user has borrowed the book previously. It also checks that the book is not already in the reading list.

- **Request Body (JSON):**
    - `book_id` (int): The ID of the book to add to the reading list (required).
    - `username` (string): The username of the user adding the book (required).
    - `email` (string): The email address of the user adding the book (required).

- **Args:**
    - `user_id` (int): The ID of the user adding the book to the reading list.

- **HTTP Response Codes:**
    - **201 Created:** If the book is successfully added to the reading list.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "book_id": 123,
            "user_id": 456,
            "message": "Book added to reading list successfully."
          }
          ```

    - **400 Bad Request:** If the request body is missing required fields or contains invalid data.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "book_id, username, email is required to add a book to reading list"
          }
          ```

    - **404 Not Found:** If the user, book, or borrowed record cannot be found.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "user not found: id, username, and/or email do not match"
          }
          ```

    - **409 Conflict:** If the book is already in the reading list or the user has not returned the borrowed book.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "message": "You must return the book before adding it to your reading list."
          }
          ```

    - **500 Internal Server Error:** For any unexpected errors during the addition process.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "An unexpected error occurred",
            "message": "Detailed error message"
          }
          ```

- **Example Request:**
  ```bash
  curl -X POST "http://example.com/users/456/read" \
    -H "Content-Type: application/json" \
    -d '{
          "book_id": 123,
          "username": "johndoe",
          "email": "johndoe@example.com"
        }'
  ```

### 2. Retrieve a User's Reading List

- **Route:** `/users/<int:user_id>/read`
- **Method:** `GET`
- **Description:** Fetches a paginated list of books from a user's reading list. The results can be filtered by various criteria such as title, author, category, publisher, language, and book ID. 

- **Args:**
    - `user_id` (int): The ID of the user whose reading list is being requested.

- **Query Parameters:**
    - `page` (int): The page number to retrieve (default is 1).
    - `per_page` (int): The number of items to return per page (default is 10).
    - `title` (string): Filter results to include books with titles matching this string (optional).
    - `author` (string): Filter results to include books by authors matching this string (optional).
    - `category` (string): Filter results to include books in this category (optional).
    - `publisher` (string): Filter results to include books published by this publisher (optional).
    - `language` (string): Filter results to include books in this language (optional).
    - `book_id` (int): Filter results to include only the book with this ID (optional).

- **HTTP Status Codes:**
    - **200 OK:** If the request is successful and the reading list is retrieved.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "read_list": [
                {
                    "book_id": 123,
                    "title": "Example Book Title",
                    "author": "John Doe",
                    "category": "Fiction"
                }
            ],
            "total_result": 1,
            "page": 1,
            "per_page": 10,
            "total_pages": 1
          }
          ```

    - **400 Bad Request:** If pagination parameters are invalid.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "Page and per_page parameters must be positive integers"
          }
          ```

    - **404 Not Found:** If no books are found matching the specified criteria.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "No Read books found matching the specified criteria"
          }
          ```

- **Errors:**
    - Invalid pagination parameters (must be positive integers).
    - Invalid or missing filtering criteria (e.g., invalid book ID).
    - No books found matching the specified criteria.

- **Returns:**
    - JSON: A JSON object containing:
        - `read_list`: A list of books in the user's reading list matching the criteria.
        - `total_result`: The total number of books found.
        - `page`: The current page number.
        - `per_page`: The number of results per page.
        - `total_pages`: The total number of pages available.

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/users/456/read?page=1&per_page=10&title=Example"
  
  ```
### 3. Remove a Book from a User's Reading List

- **Route:** `/users/<int:user_id>/read/<int:book_id>`
- **Method:** `DELETE`
- **Description:** Allows a user to remove a specified book from their reading list by providing their username and email for verification. The endpoint checks if the user and book exist before performing the deletion.

- **Args:**
    - `user_id` (int): The ID of the user from whose reading list the book will be removed.
    - `book_id` (int): The ID of the book to be removed from the reading list.

- **Request Body (JSON):**
    - `username` (string): The username of the user (required).
    - `email` (string): The email address of the user (required).

- **HTTP Status Codes:**
    - **200 OK:** If the book is successfully removed from the reading list.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "message": "Book removed from reading list successfully"
          }
          ```

    - **400 Bad Request:** If the request body is missing required fields or contains invalid data.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "username, email is required to delete a book from reading list"
          }
          ```

    - **404 Not Found:** If the user or the book is not found in the reading list.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "Book not found in reading list"
          }
          ```

    - **500 Internal Server Error:** For any unexpected errors during the deletion process.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "Error deleting book from reading list: Detailed error message"
          }
          ```

- **Errors:**
    - Invalid or missing data in the request body.
    - User not found or credentials do not match.
    - Book not found in the reading list.
    - Database errors during deletion.

- **Returns:**
    - JSON: A JSON object indicating the success or failure of the deletion operation.

- **Example Request:**
  ```bash
  curl -X DELETE "http://example.com/users/456/read/123" \
    -H "Content-Type: application/json" \
    -d '{
          "username": "johndoe",
          "email": "johndoe@example.com"
        }'
  ```
### 4. Catch-All Route for Unmatched URLs

- **Route:** `/<path:path>`
- **Method:** `GET`, `POST`, `PUT`, `DELETE`
- **Description:** This endpoint handles any requests that do not match the explicitly defined routes within the `read_list_bp` blueprint. It serves as a catch-all handler and returns a 404 error message.

- **Args:**
    - `path` (str): The unmatched path part of the URL that was requested.

- **HTTP Response Codes:**
    - **404 Not Found:** Returned when the requested URL does not match any defined route in the blueprint.
        - **Content-Type:** `application/json`
        - **Response Body:**
          ```json
          {
            "error": "The requested URL was not found on the server. Please check your spelling and try again."
          }
          ```

- **Returns:**
    - JSON: A JSON object containing an error message.

- **Example Request:**
  ```bash
  curl -X GET "http://example.com/nonexistent/path"

  ```
  ```bash
    Example Response:

    json

    {
  "error": "The requested URL was not found on the server. Please check your spelling and try again."
  }
  ```

  Notes

    Ensure to provide data in JSON format for POST and PUT requests.
  ```