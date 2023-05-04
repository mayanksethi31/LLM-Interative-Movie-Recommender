from flask import Flask, request
import json
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask_sqlalchemy import SQLAlchemy
from job_tasks import sendEmailTask, celery_app
from celery.result import AsyncResult
import re

# Initiating Flask App
app = Flask(__name__)

# Function that creates an appropriate response JSON based on message and command
def createReturnMessage(message, command=None):
    return ({"data": {"command": command, "message": message}})

def validate_email(email):
    # Regular expression for a valid email address
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # Match the email address against the regular expression
    match = re.match(pattern, email)
    # Return True if the email address is valid, False otherwise
    return bool(match)

@app.route('/execute', methods = ['POST'])
def send_email():
    try:
        data = request.data
        data = json.loads(data)
        command, message = str(data["data"]["command"]), str(data["data"]["message"])
        # Additional check to see if the command is infact "email"
        # This check is important as your Endpoint is still directly callable from outside the chatbot
        if command.lower().strip() != "email":
            return createReturnMessage("Error: Not an email command"), 400    
        try:
            to_email, subject, body = message.split(" ",2)
            if (validate_email(to_email)==False):
                return createReturnMessage("Email cannot be sent. Email id is not valid", command), 400
            emailAsyncTask = sendEmailTask.delay(to_email.strip(), subject.strip(), body.strip())
            if (emailAsyncTask.id):
                res = AsyncResult(emailAsyncTask.id, app=celery_app).get()
                if (str(res)=="202"):
                    return createReturnMessage("Email was queued. And email was sent succesfully.", command), 202
                else:
                    return createReturnMessage("Email was queued. But, email not sent due to Job or SendGrid API issue", command), 400
        except Exception as e:
            return createReturnMessage("Error: Please input all the values. Email, subject and body with spaces.", command), 400
        except:
            return createReturnMessage("Error: Something went wrong. Endpoint requires valid json input", command), 400
    except:
        return createReturnMessage("Error: Something went wrong", command), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5053, debug=True) # Running the email server on 5053