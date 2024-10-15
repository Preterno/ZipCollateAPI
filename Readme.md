# ZipCollateAPI

ZipCollateAPI is a Flask-based backend service designed to compare two ZIP files efficiently. It provides a robust API endpoint for file comparison, supporting features like password-protected ZIPs and file type exclusion.

## Features

- Fast ZIP file comparison using xxHash algorithm
- Support for password-protected ZIP files
- File type exclusion functionality
- Detailed comparison results including file presence and size information
- Secure file handling using temporary directories
- CORS support for frontend integration
- API key authentication for secure access

## Technologies Used

- Flask: A lightweight WSGI web application framework
- xxHash: Used for fast hashing to compare file contents
- CORS: Enables Cross-Origin Resource Sharing to allow requests from the frontend
- dotenv: Loads environment variables from a .env file
- zipfile: Python's built-in module for handling ZIP files
- tempfile: For secure temporary file handling
- Werkzeug: Utilities for WSGI applications, used for secure filename handling

## API Endpoint

### POST /compare_zips

Compares two ZIP files and returns detailed comparison results.

#### Request

- Method: POST
- Content-Type: multipart/form-data
- Headers:
  - X-API-KEY: Your API key

#### Form Data

- `zip1`: First ZIP file (required)
- `zip2`: Second ZIP file (required)
- `password1`: Password for the first ZIP file (optional)
- `password2`: Password for the second ZIP file (optional)
- `excludeList`: Comma-separated list of file extensions to exclude (optional)

#### Response

JSON object containing:

- `zip1_name`: Name of the first ZIP file
- `zip2_name`: Name of the second ZIP file
- `comparison`: Object with detailed file comparison results
- `exclude_list`: List of excluded file extensions

Example request:

```
curl -X POST http://localhost:5000/compare_zips \
-H "X-API-KEY: your_secret_api_key" \
-F "zip1=@path/to/zip1.zip" \
-F "zip2=@path/to/zip2.zip" \
-F "password1=your_password" \
-F "password2=your_password" \
-F "excludeList=.docx,.txt"
```

Example response:

```json
{
  "comparison": {
    "3e9ed05c-bbd9-46d0-aefe-01a6e6ea2f2a.jpeg": {
      "identical": true,
      "in_zip1": true,
      "in_zip2": true,
      "size1": "10.23 KB",
      "size2": "10.23 KB"
    },
    "Fragment.mfj": {
      "identical": false,
      "in_zip1": true,
      "in_zip2": false,
      "size1": "64.80 KB"
    },
    "TimeTable.jpeg": {
      "identical": false,
      "in_zip1": false,
      "in_zip2": true,
      "size2": "145.29 KB"
    }
  },
  "exclude_list": [".docx", ".txt"],
  "zip1_name": "zip1.zip",
  "zip2_name": "zip2.zip"
}
```

## Installation and Setup

1. Clone the repository:
   ```
   git clone https://github.com/Preterno/ZipCollateAPI.git
   cd ZipCollateAPI
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory with the following:
   ```
   API_KEY=your_secret_api_key
   ```

4. Run the Flask application:
   ```
   python app.py
   ```

The API will be available at `http://localhost:5000`.

## Configuration

- `MAX_SIZE_MB`: Maximum allowed size for ZIP files (default: 50MB)
- `allowed_origins`: List of allowed origins for CORS (update this with your frontend URL)

## Error Handling

The API returns appropriate error messages and status codes for various scenarios:

- 400 Bad Request: For invalid inputs or file issues
- 403 Forbidden: For invalid API key
- 500 Internal Server Error: For unexpected server errors

## Connect with Me

Feel free to connect with me on [LinkedIn](https://www.linkedin.com/).