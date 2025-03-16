from flask import Flask, request, jsonify
from acrcloud.recognizer import ACRCloudRecognizer
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# ACRCloud API configuration
config = {
    'host': 'identify-eu-west-1.acrcloud.com',  # Replace with your API host
    'access_key': '8584e3f555609b2e7e300df2a31bdea9',  # Replace with your Access Key
    'access_secret': 'yPrtAm6UuiyedoGNDvkSeQCjdBagUFIiHAc8SLgF',  # Replace with your Access Secret
    'timeout': 30  # Timeout in seconds
}

recognizer = ACRCloudRecognizer(config)
app = Flask(__name__)

def recognize_audio(file_name):
    logging.debug(f"Recognizing audio from {file_name}...")
    result = recognizer.recognize_by_file(file_name, 0)
    logging.debug(f"Recognition result: {result}")
    return result

@app.route('/upload', methods=['POST'])
def upload_audio():
    logging.debug("Received a request to /upload")
    logging.debug(f"Request headers: {request.headers}")
    logging.debug(f"Request form data: {request.form}")
    logging.debug(f"Request files: {request.files}")

    # Try to obtain file data from form-data first, then raw data
    file_data = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            logging.error("No selected file")
            return jsonify({"error": "No selected file"}), 400
        logging.debug(f"Received file: {file.filename}")
        file_data = file.read()
    elif request.data:
        logging.debug("No file in request.files; using raw request.data")
        file_data = request.data
    else:
        logging.error("No file uploaded")
        return jsonify({"error": "No file uploaded"}), 400

    # Save the file data to a temporary file
    temp_file_path = "uploaded_audio.wav"
    try:
        with open(temp_file_path, "wb") as f:
            f.write(file_data)
        logging.debug(f"File saved to {temp_file_path}")
    except Exception as e:
        logging.error(f"Failed to save file: {e}")
        return jsonify({"error": "Failed to save file"}), 500

    # Recognize the audio using ACRCloud
    try:
        result = recognize_audio(temp_file_path)
        logging.debug(f"Recognition result: {result}")
    except Exception as e:
        logging.error(f"Failed to recognize audio: {e}")
        try:
            os.remove(temp_file_path)
        except Exception as ex:
            logging.error(f"Failed to delete temporary file: {ex}")
        return jsonify({"error": "Failed to recognize audio"}), 500

    # Delete the temporary file after processing
    try:
        os.remove(temp_file_path)
        logging.debug(f"Deleted temporary file: {temp_file_path}")
    except Exception as e:
        logging.error(f"Failed to delete temporary file: {e}")

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
