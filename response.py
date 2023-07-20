from datetime import datetime
from flask import Flask, request
app = Flask(__name__)
@app.route('/dashboard')
def dashboard():
    start_time = datetime.now()  # Capture the start time of the request
    # Your code to process the request
    end_time = datetime.now()  # Capture the end time of the request
    response_time = (end_time - start_time).total_seconds() * 1000  # Calculate the response time in milliseconds
    return f"Response time: {response_time} ms"
if __name__ == '__main__':
    app.run()
