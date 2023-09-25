# Python Telegram Bot Quiz

[!Video demo](https://github.com/algebananazzzzz/python-telegram-bot-quiz/raw/master/demo.mp4)

## Table of Contents

- [About](#about)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Configuration](#configuration)
  - [Quiz Data Configuration](#quiz-data-configuration)
  - [Lambda Configuration](#lambda-configuration)
- [Usage](#usage)
  - [Developing Locally](#developing-locally)
- [Deployment](#deployment)
  - [Using GitHub Actions](#using-gitHub-actions-(recommended))
  - [Using Terraform Locally](#using-terraform-locally)
- [Setting Webhook](#setting-webhook)
- [License](#license)
- [Contact](#contact)

## About:

Python-Telegram-Bot-Quiz is a scalable telegram quiz bot framework built using the python-telegram-bot (v20.a4) framework. This project allows the creation of knowledge tests on multiple topics e.g. integration and logarithms in Mathematics, using telegram's native quiz feature for every question. 

With Terraform and GitHub Actions, developers can effortlessly construct QuizBots by provisioning a Lambda function with API Gateway Integration. Question configuration are stored in JSON files, enabling seamless access and modification.

## Getting Started

### Prerequisites

This project does not have any mandatory prerequisites for basic usage. You can get started without any specific requirements.

However, certain prerequisites are required if you choose to perform the following actions:

1. **Develop Telegram Bot Locally**: To run Python-Telegram-Bot locally during development phase, you must have the following tools installed:

  - **Python**: Download Python from the [official Python website](https://www.python.org/). Use Python 3.x, such as Python 3.8 or higher.
  - **PIP (Node Package Manager)**: PIP is usually included with Python installation. Make sure it's available in your Python environment.


2. **Provision Resources Locally instead**: To provision resources locally using Terraform instead of through GitHub Actions, you must have Terraform installed:
  
  - **Download Terraform**: You can download Terraform from [the official Terraform website](https://www.terraform.io/). We recommend using Terraform version 0.14.0 or higher.


### Installation

1. **Clone the Repository**:

Clone the repository to your local machine using the following command:

```shell
git clone https://github.com/algebananazzzzz/python-telegram-bot-quiz.git
cd python-telegram-bot-quiz/
```

2. **For Local Development (Optional)**

To run Python-Telegram-Bot locally during development phase, follow these additional steps to create a virtual environment, and download the required Python packages:

```shell
python3 -m venv app/
cd app/
source bin/activate
pip install -r requirements.txt
```

## Configuration:

Configuration within Python-Telegram-Bot-Quiz consists of two key aspects:

### Quiz Data Configuration. 

This involves configuring questions and answers in the `app/package/data.json` file. By referring to the JSON format within the [example](app/package/data.json) file, add on more quizzes, questions and answers as necessary.

The "answer" field designates the correct option within the "options" field, using a zero-based index, where 0 represents the first option, and so on.


### Lambda Configuration

This involves the setup and customization for the Lambda function deployed, including **Environment Variables** and **VPC Configuration**.

Under `.polymer/infrastructure.yml`, you can choose the name for Lambda Function to be deployed
```yaml
lambda:
  quizbot:
    function_name: BotName-%s-function # %s will be replaced by stage name
```

This framework includes a built-in caching layer located in [cache.py](app/package/cache.py). This feature empowers the bot to retain user quiz progress, enabling users to seamlessly continue answering quizzes even in cases of lambda destruction or interruptions.

To enable this feature, you need to provision an Amazon ElastiCache cluster with an endpoint located in a private subnet with Internet Access through NAT Gateways/Instances. Then, specify relevant stage specific **environment variables, VPC configuration, and security group configuration** under `.polymer/lambda_config/{stage}.env.json`: 


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

## Usage
### Developing Locally

With Python-Telegram-Bot, you can develop your bot locally with polling.

1. Modify .env file with environment variables and export them
```shell
cd app/
nano .env
export $(grep -v '^#' .env | xargs)
```

2. Populate data.json with quiz data. Then, check validity of quiz data with check.py.
```shell
nano package/data.json
python check.py
```

3. Run telegram bot
```
python package/main.py
```

## Deployment

### Using GitHub Actions (Recommended)

1. **Create a GitHub Repository:**
Start by creating a GitHub repository. After that, follow these steps to initialize Git and switch to the `dev` branch:
```
git init
git add -A
git commit
git checkout -b dev
git remote set-url origin https://github.com/{your_repository_name}.git
```

2. **Configure Secrets and Variables:**

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

3. **Push to GitHub**
```shell
git push --set-upstream origin dev
```

With GitHub Actions in place, this push will automatically trigger the following processes:

- Webpack will bundle your Node.js code, optimizing it for production deployment.

- If a workspace for your organization doesn't already exist, Terraform Cloud will create one.Terraform Cloud will then be triggered to provision the necessary resources according to your infrastructure configuration. 


4. **Staging**

After a successful deployment of the dev branch, you can extend the same workflow to deploy your application to other stages, such as **test** or **production**. Follow these steps for each stage:

- Create a new branch corresponding to the stage you want to deploy (e.g., `test`, `prod`).
- Merge the `dev` branch into the newly created stage branch. 

This push to the stage branch will automatically trigger GitHub Actions to provision resources for the specified stage. Repeat these steps for each stage as needed, allowing you to deploy your application to multiple environments seamlessly.


### Using Terraform Locally

If you prefer to use Terraform locally and avoid pushing code to GitHub, you can follow these steps. This approach offers several benefits, including greater control and flexibility over your infrastructure provisioning.

1. **Check Terraform Version**:

    After downloading Terraform, verify its version to ensure it's correctly installed:

     ```shell
     terraform -v
     ```
     
2. **Update terraform.tf Configuration**:

Modify the `terraform.tf` configuration file to specify the required Terraform version under the `required_version` block, and comment out the "cloud" block:

```hcl
terraform {
  required_version = "~>1.5.0"

    # cloud {
    #   workspaces {
    #     tags = ["github-actions"]
    #   }
    # }

  # Other configuration settings...
}
```

3. **Specify Staging Environment**:

To define the staging environment you intend to work with, set the `STAGE` variable:

```shell
export STAGE=dev
```

4. **Bundle Node.js files with Webpack**
To bundle your Node.js files using Webpack, optimizing it for production deployment:

```shell
cd api/
npm run build
```

5. **Terraform Init, Plan and Apply**:

```shell
terraform init
terraform plan
terraform apply --auto-approve
```


## Setting Webhook

To make your bot respond to requests from Telegram users, you have two options:

1. Manually request updates from the Telegram Bot API, done when developing the bot locally
2. Register a webhook to automatically receive calls when updates are available. 

With the provisioned resources, you can opt for the latter option to maintain the bot's production uptime. Copy the API Gateway Integration URL from the Terraform output, and then replace the appropriate fields in the URL below. Finally, paste this modified URL into your web browser to register the webhook.


```url
https://api.telegram.org/bot{my_bot_token}/setWebhook?url={url_to_send_updates_to}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
[Provide a way for users to contact you, whether it's an email address, a link to your website, or social media profiles.]


## Contact

For inquiries and further information, feel free to reach out to me through my [portfolio page](https://www.algebananazzzzz.com).
