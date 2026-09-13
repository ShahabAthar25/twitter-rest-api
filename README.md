# Twitter API Clone

The **_Twitter API Clone_**, is made by me, Shahab Athar, it is a complete replication of the functionalities of the original Twitter API. This API provides a robust platform for user interaction, content sharing, and social networking. It has **_JWT authentication with rolling access and refresh tokens_**, allowing users to register, login, and reset passwords. Users can **_authenticate with username and password_**. Users can **_manage their profiles, follow or unfollow others, and search for users by various criteria_**. The API supports creating **_tweets, replying to tweets with nested replies, and bookmarking tweets_** for future reference. Additionally, users can create and manage **_Twitter lists_** to curate groups of users for targeted content viewing. Additionally, there is an **_admin panel_** for managing users and overseeing the platform. The **_API comprises of 36+ endpoints_** covering a wide range of functionalities, enhancing user interaction and engagement. Future enhancements include the introduction of community features and real-time messaging using Django Channels, aiming to provide an enriched social media experience.

## Installation

To setup the the twitter api clone, make sure that **python, pip and git are installed**.

### Clone the repository

Before doing anything let's make sure you have cloned this repository. Clone the repository by running the following command

```bash
git clone https://github.com/ShahabAthar25/Twitter-Django-NextJS.git
```

### Setup vitual enviroment

We will create the vitual enviroment using _virtualenv_ package. Feel free to use any other library. Install virtualenv by using the following commands

```bash
# using pip
pip install virtualenv

# Using pacman (If you use arch you rock!!!)
sudo pacman -Sy python-virtualenv
```

To create virtual enviroment using virtualenv

```py
vitualenv venv
```

Now, activate the enviroment

```bash
./venv/bin/activate
```

### Install Dependencies

All the dependencies that are used by this _Twitter API Clone_ are listed in the requirements.txt. Install it by running the following command

```py
python install -r requirements.txt
```

### Setting up .env file

We need to setup the .env file in order to access our secret key which is stored in **.env** file and not in settings.py. First copy the .env template or rename it as .env

```bash
# copy .env.template file to .env
cp .env.template .env
```

Now, all you need to do is set your **SECRET_KEY** in the **.env** file. To generate a secret key open the python shell by running the following command

```bash
# Open up the python shell
python
```

Generate the secret in python using **secrets** module. Feel free to use any other method or library.

```py
# Generate the secret key
import secrets
secrets.token_hex(32)
```

Now copy the output to your **SECRET_KEY** variable in your **.env**

### Making super user (Optional)

If you want to access the admin panel, you will need a super user. This step is optional as the **Twitter API Clone** can run without creating one. To create a super user, run the following command

```py
python manage.py createsuperuser
```

Now, fill out the credentials of the super user. It will ask for the following information.

- **Username**
- **Email**
- **First name**
- **Last name**
- **Password**
- **Confirm password**

### Setup database and make migrations

Before running the _Twitter API Clone_ we have to make sure our database is created and running. We are using **sqlite** as database but feel free to change it to any other database like sql, postgres etc. in **settings.py**. Setup databse by the following commands

```bash
# Change present working directory to backend
cd ./backend/

# Migrate the database
python manage.py migrate
```

### Running the API

To run the api make sure you have performed the above mentioned steps. Now, run the api with the following command

```py
python manage.py runserver
```

## Documentation

Visit the following url for the complete documentation of this **Twitter API Clone**: [https://documenter.getpostman.com/view/28992075/2sA3Qs8rfZ](https://documenter.getpostman.com/view/28992075/2sA3Qs8rfZ)
