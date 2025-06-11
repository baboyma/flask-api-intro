import os
import io
import uuid
import pandas as pd
from flask import Flask, request, jsonify, abort
from werkzeug.utils import secure_filename

# Initialize the Flask application
app = Flask(__name__)

# In-memory store for our DataFrames.
# In a real-world production application, this should be replaced with a persistent database
# (e.g., SQLite, PostgreSQL, MongoDB, or even a cloud storage like S3/GCS with metadata in a DB).
# The key will be the unique dataset_id (UUID), and the value will be the pandas.DataFrame.
DATA_STORE = {}

# Allowed file extensions for uploads to ensure only CSVs are processed.
ALLOWED_EXTENSIONS = {'csv'}

# Helper function to validate file extension
def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """
    Renders a simple HTML page for uploading CSV files and shows available datasets.
    This acts as a basic UI for demonstration.
    """
    # List current dataset IDs for user reference
    current_datasets = ', '.join(DATA_STORE.keys()) if DATA_STORE else 'None'
    return f"""
    <!doctype html>
    <title>Upload CSV for API Endpoint</title>
    <style>
        body {{ font-family: 'Inter', sans-serif; margin: 2rem; background-color: #f0f4f8; color: #333; }}
        h1 {{ color: #2c3e50; margin-bottom: 1.5rem; }}
        form {{
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-width: 500px;
        }}
        input[type="file"] {{
            border: 1px solid #ccc;
            padding: 0.5rem;
            border-radius: 4px;
            background-color: #fafafa;
        }}
        input[type="submit"] {{
            background-color: #3498db;
            color: white;
            padding: 0.75rem 1.25rem;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s ease;
        }}
        input[type="submit"]:hover {{
            background-color: #2980b9;
        }}
        p {{ margin-top: 1rem; font-size: 0.9em; color: #555; }}
        code {{ background-color: #e8e8e8; padding: 0.2em 0.4em; border-radius: 3px; font-family: monospace; }}
    </style>
    <body>
        <h1>Upload a CSV File to Create an API Endpoint</h1>
        <form method="post" enctype="multipart/form-data" action="/upload">
          <label for="file-upload" class="sr-only">Choose CSV File</label>
          <input id="file-upload" type="file" name="file" accept=".csv">
          <input type="submit" value="Upload CSV">
        </form>
        <p>Once uploaded, your data will be accessible via:</p>
        <ul>
            <li><code>/data/&lt;dataset_id&gt;</code> (to retrieve all data)</li>
            <li><code>/data/&lt;dataset_id&gt;/filter?column_name=value&another_col=value</code> (to filter data)</li>
        </ul>
        <p>Currently available datasets: <code>{current_datasets}</code></p>
    </body>
    </html>
    """

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handles CSV file uploads.
    Reads the CSV into a pandas DataFrame and stores it in memory with a unique ID.
    Returns the dataset_id and URLs for accessing the new API endpoint.
    """
    # Check if a file was included in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files['file']

    # Check if a file was selected
    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    # Validate file extension
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed. Only CSV files are accepted."}), 400

    if file:
        try:
            # Read the file content directly into a Pandas DataFrame without saving to disk.
            # io.StringIO is used to treat the in-memory file stream as a text file for pandas.
            file_content = io.StringIO(file.read().decode('utf-8'))
            df = pd.read_csv(file_content)

            # Generate a universally unique ID for this new dataset.
            dataset_id = str(uuid.uuid4())
            DATA_STORE[dataset_id] = df

            # Return success response with access details
            return jsonify({
                "message": "CSV uploaded and exposed as API endpoint successfully!",
                "dataset_id": dataset_id,
                "access_url": f"/data/{dataset_id}",
                "filter_url_example": f"/data/{dataset_id}/filter?your_column_name=value"
            }), 201 # 201 Created status code
        except Exception as e:
            # Catch any errors during file processing (e.g., malformed CSV)
            app.logger.error(f"Error processing CSV: {e}")
            return jsonify({"error": f"Failed to process CSV: {str(e)}. Please check file format."}), 500

@app.route('/data/<string:dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """
    Retrieves the entire dataset associated with the given dataset_id.
    Returns the data as a JSON array of objects.
    """
    df = DATA_STORE.get(dataset_id)
    if df is None:
        # If dataset_id is not found, return 404 Not Found
        abort(404, description="Dataset not found. Please check the dataset ID or upload a CSV first.")

    # Convert the pandas DataFrame to a list of dictionaries, suitable for JSON output.
    # 'orient='records'' ensures each row becomes a dictionary.
    return jsonify(df.to_dict(orient='records'))

@app.route('/data/<string:dataset_id>/filter', methods=['GET'])
def filter_dataset(dataset_id):
    """
    Filters the dataset based on query parameters provided in the URL.
    Example: /data/{id}/filter?City=New York&Age=30
    Filters are applied as exact matches.
    """
    df = DATA_STORE.get(dataset_id)
    if df is None:
        abort(404, description="Dataset not found. Please check the dataset ID or upload a CSV first.")

    # Get all query parameters from the request (e.g., {'City': 'New York', 'Age': '30'})
    filters = request.args.to_dict()

    # Work on a copy of the DataFrame to avoid modifying the original data in DATA_STORE
    filtered_df = df.copy()

    for column, value in filters.items():
        if column not in filtered_df.columns:
            # If a filter column doesn't exist in the DataFrame, skip it.
            # You could choose to return an error here instead, depending on desired behavior.
            app.logger.warning(f"Filter column '{column}' not found in dataset {dataset_id}.")
            continue

        # Apply the filter. This attempts to handle both string and numeric comparisons.
        # It converts the DataFrame column and the filter value to string for comparison,
        # and also attempts numeric conversion for numeric columns.
        try:
            # Attempt to convert column to numeric and compare, if that fails,
            # fall back to string comparison. 'errors='coerce'' turns non-numeric
            # values into NaN, allowing the comparison to proceed without error.
            filtered_df = filtered_df[
                (filtered_df[column].astype(str) == value) |
                (pd.to_numeric(filtered_df[column], errors='coerce') == pd.to_numeric(value, errors='coerce'))
            ]
        except ValueError:
            # If `pd.to_numeric` itself raises a ValueError for the filter `value`,
            # then just proceed with string comparison for the column.
            filtered_df = filtered_df[filtered_df[column].astype(str) == value]
        except Exception as e:
            # Catch any other unexpected errors during filtering
            app.logger.error(f"Error applying filter on column '{column}' for dataset {dataset_id}: {e}")
            return jsonify({"error": f"Error applying filter on column '{column}': {str(e)}"}), 500

    if filtered_df.empty:
        # If no rows match the filter criteria, return an empty response with a message
        return jsonify({"message": "No data matches your filter criteria."}), 200

    # Return the filtered data as a JSON array of objects
    return jsonify(filtered_df.to_dict(orient='records'))

if __name__ == '__main__':
    # This runs the Flask development server.
    # For production deployment, use a production-ready WSGI server like Gunicorn or uWSGI.
    # debug=True provides helpful error messages during development.
    app.run(debug=True, port=5000)
