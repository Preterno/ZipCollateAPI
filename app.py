from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import os
import zipfile
import tempfile
from xxhash import xxh64
from werkzeug.utils import secure_filename
from functools import partial

app = Flask(__name__)
CORS(app, resources={r"/compare_zips": {"origins": "*"}})

MAX_SIZE_MB = 50

def format_file_size(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0
    return f"{size_in_bytes:.2f} TB"

def get_file_extension(file):
    return os.path.splitext(file)[1][1:]

def is_zip_encrypted(zip_file):
    try:
        zip_file.testzip()
        return False
    except RuntimeError:
        return True

def zip_comparison(zip1_path, zip2_path, password1, password2, exclude_list):
    try:
        for zip_path in (zip1_path, zip2_path):
            size_mb = os.path.getsize(zip_path) / (1024 * 1024)
            if size_mb > MAX_SIZE_MB:
                raise ValueError(f"One or both ZIP files exceeds {MAX_SIZE_MB}MB limit")

            if not zipfile.is_zipfile(zip_path):
                raise ValueError(f"One or both files are not a valid zip file")

        with zipfile.ZipFile(zip1_path, 'r') as zip1, zipfile.ZipFile(zip2_path, 'r') as zip2:
            if is_zip_encrypted(zip1) and not password1:
                raise ValueError("First zip file is password-protected but no password was provided")
            if is_zip_encrypted(zip2) and not password2:
                raise ValueError("Second zip file is password-protected but no password was provided")

            try:
                open_zip1 = partial(zip1.open, pwd=password1.encode() if password1 else None)
                open_zip2 = partial(zip2.open, pwd=password2.encode() if password2 else None)
                
                files1 = set(zip1.namelist())
                files2 = set(zip2.namelist())

                file_comparison = {}
                exclude_set = set(exclude_list)

                for file in files1.union(files2):
                    file_extension = '.'+get_file_extension(file).lower()
                    if file_extension in exclude_set:
                        continue

                    comparison = {"in_zip1": file in files1, "in_zip2": file in files2, "identical": False}
                    
                    if comparison["in_zip1"]:
                        size1 = zip1.getinfo(file).file_size
                        comparison["size1"] = format_file_size(size1)
                    
                    if comparison["in_zip2"]:
                        size2 = zip2.getinfo(file).file_size
                        comparison["size2"] = format_file_size(size2)

                    if comparison["in_zip1"] and comparison["in_zip2"]:
                        if size1 == size2:
                            with open_zip1(file) as f1, open_zip2(file) as f2:
                                hash1 = xxh64(f1.read()).hexdigest()
                                hash2 = xxh64(f2.read()).hexdigest()
                                comparison["identical"] = hash1 == hash2

                    file_comparison[file] = comparison

                return file_comparison

            except RuntimeError as e:
                if "Bad password" in str(e):
                    raise ValueError("Incorrect password provided for one of the zip files")
                else:
                    raise

    except Exception as e:
        raise ValueError(f"Error during zip comparison: {str(e)}")


@app.route('/compare_zips', methods=['POST', 'OPTIONS'])
def compare_zips():
    if request.method == "OPTIONS":
        return _build_cors_preflight_response()
    elif request.method == "POST":
        try:
            if 'zip1' not in request.files or 'zip2' not in request.files:
                return jsonify({"error": "Missing zip files"}), 400

            zip1 = request.files['zip1']
            zip2 = request.files['zip2']

            if zip1.filename == '' or zip2.filename == '':
                return jsonify({"error": "No selected files"}), 400

            if not zip1.filename.endswith('.zip') or not zip2.filename.endswith('.zip'):
                return jsonify({"error": "Both files must be zip files"}), 400

            if zip1.content_length > MAX_SIZE_MB * 1024 * 1024 or zip2.content_length > MAX_SIZE_MB * 1024 * 1024:
                return jsonify({"error": f"One or both ZIP files exceeds {MAX_SIZE_MB}MB limit"}), 400

            password1 = request.form.get('password1', None)
            password2 = request.form.get('password2', None)
            exclude_str = request.form.get('excludeList', '')
            exclude_list = [item.strip() for item in exclude_str.split(',')] if exclude_str else []

            with tempfile.TemporaryDirectory() as temp_dir:
                zip1_path = os.path.join(temp_dir, secure_filename(zip1.filename))
                zip2_path = os.path.join(temp_dir, secure_filename(zip2.filename))
                
                zip1.save(zip1_path)
                zip2.save(zip2_path)

                result = zip_comparison(zip1_path, zip2_path, password1, password2, exclude_list)

                return jsonify({
                    "zip1_name": zip1.filename,
                    "zip2_name": zip2.filename,
                    "comparison": result,
                    "exclude_list":exclude_list,
                })

        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": "An unexpected error occurred. Please try again later."}), 500

def _build_cors_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

if __name__ == '__main__':
    app.run(debug=False)