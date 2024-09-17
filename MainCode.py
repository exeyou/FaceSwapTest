from flask import Flask, request, redirect, url_for
import requests
import time

app = Flask(__name__)

# Replace with your actual API key
API_KEY = "cm13mpgl20007mh03348pu3wy"
UPLOAD_URL = "https://api.magicapi.dev/api/v1/capix/faceswap/upload/"
SWAP_URL = "https://api.magicapi.dev/api/v1/capix/faceswap/faceswap/v1/image"
RESULT_URL = "https://api.magicapi.dev/api/v1/capix/faceswap/result/"

@app.route('/')

def upload_to_api(file):
    boundary = "----011000010111000001101001"
    payload = (
        f"--{boundary}\r\n"
        f"Content-Disposition: form-data; name=\"file1\"; filename=\"{file.filename}\"\r\n"
        f"Content-Type: {file.content_type}\r\n\r\n"
    ).encode('utf-8') + file.read() + f"\r\n--{boundary}--\r\n".encode('utf-8')

    headers = {
        'x-magicapi-key': MAGIC_API_KEY,
        'content-type': f"multipart/form-data; boundary={boundary}"
    }

    conn = http.client.HTTPSConnection("api.magicapi.dev")
    conn.request("POST", "/api/v1/capix/faceswap/upload/", payload, headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()

    return data.decode('utf-8')
    
def upload_form():
    # Render a form to upload two image files
    return '''
    <!doctype html>
    <title>Face Swap API</title>
    <h1>Face Swap via Image Files</h1>
    <form method="POST" action="/upload" enctype="multipart/form-data">
      <label for="file1">Target Image (Upload):</label><br>
      <input type="file" id="file1" name="file1" accept="image/*"><br><br>
      
      <label for="file2">Swap Image (Upload):</label><br>
      <input type="file" id="file2" name="file2" accept="image/*"><br><br>
      
      <input type="submit" value="Upload and Swap Faces">
    </form>
    '''
def upload_file(file):
    """Helper function to upload an image file and get its URL."""
    files = {
        'file1': (file.filename, file, file.content_type)
    }

    headers = {
        'x-magicapi-key': API_KEY,
        'Content-Type': 'multipart/form-data; boundary=---011000010111000001101001'
    }

    response = requests.post(UPLOAD_URL, files=files, headers=headers)

    if response.status_code == 200:
        # Extract the URL from the response (the response contains only the URL)
        return response.json()
    else:
        return None

@app.route('/upload', methods=['POST'])
def upload_images():
    # Get the files from the form
    file1 = request.files.get('file1')
    file2 = request.files.get('file2')

    if not file1 or not file2:
        return 'Both files must be uploaded.'

    # Upload the first file and get its URL
    target_url = upload_file(file1)
    if not target_url:
        return 'Failed to upload the target image.'

    # Upload the second file and get its URL
    swap_url = upload_file(file2)
    if not swap_url:
        return 'Failed to upload the swap image.'

    # Once we have both URLs, initiate face swap
    return redirect(url_for('face_swap', target_url=target_url, swap_url=swap_url))

@app.route('/swap')
def face_swap():
    # Get the image URLs from the query parameters
    target_url = request.args.get('target_url')
    swap_url = request.args.get('swap_url')

    if not target_url or not swap_url:
        return 'Target URL and Swap URL are required.'

    # Prepare the payload for the face swap API request
    payload = f"target_url={target_url}&swap_url={swap_url}"

    headers = {
        'x-magicapi-key': API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Make the POST request to the API for face swapping
    response = requests.post(SWAP_URL, data=payload, headers=headers)

    if response.status_code == 200:
        json_response = response.json()

        # Extract the request_id from the API response
        request_id = json_response.get('image_process_response', {}).get('request_id')

        if request_id:
            # Redirect to the result-checking route
            return redirect(url_for('check_result', request_id=request_id))
        else:
            return 'Failed to get request_id from the API response.'
    else:
        return f'Failed! Status Code: {response.status_code}, Response: {response.text}'

@app.route('/result/<request_id>')
def check_result(request_id):
    # Prepare the payload for the API request (URL encoded)
    payload = f"request_id={request_id}"

    headers = {
        'x-magicapi-key': API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Give the API some time to process the images (optional)
    time.sleep(2)

    # Make the POST request to check the result
    response = requests.post(RESULT_URL, data=payload, headers=headers)

    if response.status_code == 200:
        result_response = response.json()

        # Display the API response to the user
        return f'Success! Face Swap Result: {result_response}'
    else:
        return f'Failed! Status Code: {response.status_code}, Response: {response.text}'

if __name__ == '__main__':
    app.run(debug=True)
