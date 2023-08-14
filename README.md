# Python Telegram Bot Quiz

[!Video demo](demo.mp4)

## Table of Contents

- [About](#about)
- [Configuration](#configuration)
- [Resources](#resources)
- [Quiz Data Configuration](#quiz)
- [Deploying Locally](#deploying)
- [Deploying with AWS](#deploying)
- [License](#license)
- [Contact](#contact)

## About:

Python-Telegram-Bot-Quiz is a scalable telegram quiz bot framework built using the python-telegram-bot (v20.a4) framework. This project allows the creation of knowledge tests on multiple topics e.g. integration and logarithms in Mathematics, using telegram's native quiz feature for every question. 

Integrated with Terraform and GitHub Actions, empowering developers to effortlessly construct QuizBots using AWS Serverless resources. Employed a user-friendly approach by storing question configurations in JSON files, enabling seamless access and modification.


## Configuration:

Configuration within Python-Telegram-Bot-Quiz consists of two key aspects:

1. Quiz Data Configuration. Configure Questions and Answers through `app/deploy/data.json`.

2. Resource Configuration: This involves the setup and customization of the resources deployed, including API Gateway and Lambda.


## Resources

Here are the resources that will be deployed, along with instructions on how to configure them:

1. **Lambda Function** to respond to requests.

Under `.polymer/infrastructure.yml`, you can choose the name for Lambda Function to be deployed
```yaml
lambda:
  botname:
    function_name: BotName-%s-function # %s will be replaced by stage name
    basedir: app/deploy
    envfile_basedir: .polymer/lambda_config
```

Under `.polymer/lambda_config/{stage}.env.json`, you can configure the stage specific configuration e.g. Environment Variables, VPC. Here are the compulsory configurations, and what they represent.

```json
{
    "environment_variables": {
        "PASSPHRASE": "password to be presented to access quiz (optional)", 
        "REDIS_HOST": "host endpoint in VPC e.g. cluster.abc.cache.amazonaws.com",
        "REDIS_KEY": "key to store application cache e.g. BotQuizData",
        "REDIS_PORT": 6379,
        "START_MESSAGE": "Message to be presented on /start",
        "TOKEN": "bot token from @BotFather"
    },
    "vpc_config": {
        "subnet_ids": [
            "ElastiCache's subnet ID where it is currently operational"
        ],
        "security_group_ids": [
            "Security Group to allow traffic to ElastiCache cluster"
        ]
    },
}
```

2. **API Gateway** Integration.

In the .polymer/infrastructure.yml file, ensure that you define an integration that corresponds to the Lambda function.

```yaml
api_lambda_integration:
  botname:
    integration: true
```

## Quiz Data Configuration:
Configure the quiz data within the app/deploy/data.json file.


The "answer" field designates the correct option within the "options" field, using a zero-based index, where 0 represents the first option, and so on.

```json
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


## Deploying Locally (with polling)
1. Git clone this repository
```shell
git clone https://github.com/algebananazzzzz/python-telegram-bot-quiz.git
cd python-telegram-bot-quiz/
```

2. Install necessary python packages into virtual environment
```shell
python3 -m venv app/
pip install -r app/requirements.txt
```

3. Modify .env file with environment variables
```shell
cd app/development/
nano .env
```

4. Populate data.json with quiz data. For information of syntax for data.json, please refer to above.
```shell
nano data.json
```

Then, check validity of quiz data with check.py.
```shell
python check.py
```

4. Run telegram bot
```
export $(grep -v '^#' .env | xargs)
python main.py
```


## Deploying with AWS
1. **Prepare deployment package**
Copy Quiz Data Configuration into `deploy` folder, and install necessary packages:

```shell
cd ../
cp development/data.json deploy/data.json
pip install -r requirements.txt -t deploy/
```

2. **Create a GitHub Repository:**
Create a GitHub repository. After that, follow these steps to initialize Git and switch to the `dev` branch:
```shell
cd ../
git init
git add -A
git commit
git checkout -b dev
git remote set-url origin https://github.com/{your_repository_name}.git
```

3. **Configure Secrets and Variables:**

For secure and streamline access to AWS and Terraform Cloud, follow these steps to configure secrets and variables within your GitHub repository:

- Click on the `Settings` tab within your repository.
- Navigate to `Secrets` (or `Environments` > `Secrets` depending on your GitHub version).
- Click on `New repository secret` to add secrets or `New repository variable` to add variables.

**Required Secrets:**

1. `AWS_ACCESS_KEY_ID`: Your AWS access key ID.
2. `AWS_SECRET_ACCESS_KEY`: Your AWS secret access key.
3. `TF_API_TOKEN`: Obtain this token by going to your [Terraform Cloud tokens page](https://app.terraform.io/app/settings/tokens).

**Required Variables:**

1. `APPLICATION_NAME`: Set your application's name.
2. `AWS_REGION`: Define the AWS region you're working with.
3. `TF_ORGANISATION`: If not already created, create a Terraform Cloud organization for use.


4. **Push to GitHub**
```shell
git push --set-upstream origin dev
```

With GitHub Actions in place, this push will automatically trigger Terraform Cloud to provision the necessary resources.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
[Provide a way for users to contact you, whether it's an email address, a link to your website, or social media profiles.]


## Contact

For inquiries and further information, feel free to reach out to me through my [portfolio page](https://www.algebananazzzzz.com).