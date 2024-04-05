from flask import Flask, request, jsonify,send_from_directory
import subprocess
from subprocess import Popen,check_output
import os
import time
import socket
import re

app = Flask(__name__)


@app.route('/check')
def hello_world():
    return 'Hello, World! This is my Flask backend.'

@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.get_json()  # Get JSON data from the request
    return jsonify(data)  # Echo back the JSON data

@app.route('/aerial', methods=['POST'])
def aerial():
    # Check if the request contains a file
    if 'image' not in request.files:
        return 'No file part', 400
    
    # Get the file from the request
    file = request.files['image']
    
    # Check if the file is empty
    if file.filename == '':
        return 'No selected file', 400
    
    # Save the file to the /uploads folder
    file.save('uploads/' + file.filename)

    process = Popen(["python", "detect.py", '--source', "uploads/"+file.filename, "--weights","aerial.pt" , "--save-txt", "--exist-ok"], shell=True)
    process.wait()

    
    # Get the hostname of the PC
    hostname = socket.gethostname()
    # Get the IP address corresponding to the hostname
    ip_address = socket.gethostbyname(hostname)
    ImageUrl = "http://"+ip_address +":8081/images/"+file.filename
    print(ImageUrl)

    # Remove the .jpg extension
    filename_without_extension = file.filename[:-4]
    
    filename_with_txt_extension = filename_without_extension + ".txt"

   # Initialize a variable to count the lines
    line_count = 0
    # Open the file and iterate over its lines
    with open("runs/detect/exp/labels/"+filename_with_txt_extension, 'r') as file:
        for line in file:
            line_count += 1
    print(line_count)

    # Construct the JSON response
    response = {
        "ImageUrl": ImageUrl,
        "Description": f"{line_count} trees detected"
    }
    
    # Return the JSON response
    return jsonify(response), 200

@app.route('/ground', methods=['POST'])
def ground():
    # Check if the request contains a file
    if 'image' not in request.files:
        return 'No file part', 400
    
    # Get the file from the request
    file = request.files['image']
    
    # Check if the file is empty
    if file.filename == '':
        return 'No selected file', 400
    
    # Save the file to the /uploads folder
    file.save('uploads/' + file.filename)

    out = check_output(["python", "detect.py", '--source', "uploads/"+file.filename, "--weights","best.pt" , "--save-txt", "--exist-ok"], shell=True)
   
    
    # Split the output by line breaks
    output_lines = out.decode('utf-8').split('\r\n')

    line_parts = output_lines[len(output_lines)-4].split(',')
    
    # Get the hostname of the PC
    hostname = socket.gethostname()
    # Get the IP address corresponding to the hostname
    ip_address = socket.gethostbyname(hostname)
    ImageUrl = "http://"+ip_address +":8081/images/"+file.filename
    print(ImageUrl)
    
    # Construct the JSON response
    response = {
        "ImageUrl": ImageUrl,
        "Description": f"{line_parts[0]} detected"
    }
    
    # Return the JSON response
    return jsonify(response), 200

@app.route('/images/<filename>')
def serve_image(filename):
    directory = 'runs/detect/exp/'
    return send_from_directory(directory, filename)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081)  # debug=True causes Restarting with stat