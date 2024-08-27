# Book Library API

## Project Overview

The **Book Library API** is a RESTful API designed for managing a book library system. It allows users to:
- **Search for Books:** Query the library database to find books based on various criteria.
- **Check Availability:** Check the availability status of books.
- **Borrow or Return Books:** Manage the borrowing and returning of books.
- **Manage Reading Lists:** Create and manage personal reading lists.

## Features

- **Book Management:** Add, update, and delete book records.
- **User Management:** Register, authenticate, and manage user profiles.
- **Book Availability:** Check if books are available for borrowing.
- **Borrowing System:** Handle book borrowing and returning operations.
- **Reading Lists:** Create and manage personal reading lists.

## Technologies Used

- **Flask:** Web framework for building the API.
- **MySQL:** Relational database management system for storing book and user data.
- **SQLAlchemy:** ORM for database interactions.
- **Flask-Migrate:** Tool for handling database migrations.
- **Postman:** For API testing.

## Installation

### Prerequisites

- Python 3.7 or higher
- MySQL server
- pip (Python package installer)

### Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/book-library-api.git
   cd book-library-api

2. **Create and Activate a Virtual Environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt