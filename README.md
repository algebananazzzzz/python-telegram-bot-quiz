# Python Telegram Bot Quiz

![Video demo](https://user-images.githubusercontent.com/48286805/235227846-71e991c6-b58a-44e9-813a-c206652d104a.mp4)

Writeup:

A scalable telegram quiz bot built using the python-telegram-bot (v20.1) framework. This project allows the creation of knowledge tests on multiple topics e.g. integration and logarithms in Mathematics, using telegram's native quiz feature 

for every question. This allows users to test themselves anywhere, anytime using a familiar interface with ease.


# Deployment Requisites:
This project supports local deployment with python3 and redis installed, and cloud deployment with AWS Lambda and Elasticache configured in VPCs

## Deploying Locally (with polling)
Set up:
1. Git clone this repository
```
git clone https://github.com/algebananazzzzz/python-telegram-bot-quiz.git
cd python-telegram-bot-quiz
```

2. Create .env file with environment variables
```
cat > .env
TOKEN=<bot token obtained from BotFather>
REDIS_KEY=<Key to store persistence as in Redis>
REDIS_HOST=<localhost>
REDIS_PORT=<Default port for Redis is 6379>
START_MESSAGE=<your message to send on /start here (optional)>
PASSPHRASE=<to limit access to quizzes (optional)>
```
3. Populate data.json with quiz data. For information of syntax for data.json, please refer below.
```
nano data.json
```
Then, check validity of quiz data with check.py.
```
python check.py
```
4. Run telegram bot
```
export $(grep -v '^#' .env | xargs)
python main.py
```

## Deploying with AWS
Set up:
1. Git clone this repository to your local machine
```
git clone https://github.com/algebananazzzzz/python-telegram-bot-quiz.git
cd python-telegram-bot-quiz
```
2. Populate data.json with quiz data and check validity
```
nano data.json
python check.py
```
3. Install dependencies locally, and create a zip file with dependencies (or use Lambda Layers) + code
```
pip install -r requirements.txt -t python/
cd python/
zip -r ../deployment_package.zip .
cd ../
zip deployment_package.zip lambda_function.py
zip deployment_package.zip handlers.py
zip deployment_package.zip mypersistence.py
zip deployment_package.zip data.json
```
4. Configure a Lambda Function (python3) within a public subnet with internet access, with routing to a private subnet with Elasticache Redis node(s) and deploy zip file to Lambda. Add environment variables listed above and an API trigger to the function, then set webhook to the API URL.

# data.json syntax

Syntax comprises of quizzes organised in a list. The "answer" field specifies which option is correct in the "options" field, with 0 being the first option etc.
```
[{
  "quiz_name": "Section A",
  "quiz_data": {
    "Question 1": {
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "answer": 0
    },
    "Question 2": {
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "answer": 1
    },
    "Question 3": {
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "answer": 2
    }
  }
}, {
  "quiz_name": "Section B",
  "quiz_data": {
    "Question 1": {
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "answer": 0
    },
    "Question 2": {
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "answer": 1
    },
    "Question 3": {
      "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
      "answer": 2
    }
  }
}]
```
