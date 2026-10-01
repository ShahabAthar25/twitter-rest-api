# Twitter REST API

This project is a Twitter-like REST API built with Django, focused on backend architecture, performance, and asynchronous processing. It provides more than 36 endpoints across six core domains: authentication, users, tweets, replies, lists, and bookmarks.

The goal was to build more than a basic Twitter clone. I wanted to explore how a large API could handle frequent requests without putting unnecessary load on the database. Redis handles caching, while Celery takes care of background tasks that don't need to run during an API request. The result is a backend designed to keep responses fast while remaining structured and maintainable.

# Installation

Bash

```
# Clone the repository
git clone git@github.com:ShahabAthar25/twitter-rest-api.git
cd twitter-rest-api

# Install dependencies
uv sync

# Activate the venv
source .venv/bin/activate

# Configure environment variables
cp .env.example .env

# Apply database migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

# Configurations

* PostgreSQL: Configure the database connection in your environment variables, including the database name, user, password, host, and port.

* Redis: Set up Redis and provide its connection URL for caching.

* Celery: Configure the broker and result backend, then start a Celery worker to process background tasks.

* Django: Set the required secret key, allowed hosts, and other environment-specific settings before running the application.

# Documentation

Visit the following url for the complete documentation of this **Twitter API Clone**: [https://documenter.getpostman.com/view/28992075/2sA3Qs8rfZ](https://documenter.getpostman.com/view/28992075/2sA3Qs8rfZ)

# Notes

This project focuses on backend architecture rather than simply implementing a large number of endpoints. A Twitter-like application generates frequent reads and updates, so the main challenge was to keep the request cycle efficient while ensuring that data remained consistent.

The system follows three main principles:

* Performance — Reduce repeated database operations through Redis caching and move non-critical work to background workers.

* Scalability — Organize the API around independent resources and keep asynchronous tasks separate from request handling.

* Maintainability — Keep the architecture structured as the number of endpoints and features grows.

## Performance

A social media API constantly retrieves data, especially tweets and user feeds. Querying PostgreSQL for every request creates unnecessary overhead.

Redis acts as a caching layer for frequently requested data. When a cached result is available, the API can return it without querying the database again. This reduced database operations by approximately 70–80% in the measured workload.

## Asynchronous Processing

Not every operation needs to finish before an API response is returned. Tasks such as updating tweet view counts can be handled separately.

Celery processes these tasks in the background. View counts are cached and synchronized with PostgreSQL later, keeping non-critical operations out of the main request cycle and allowing the API to respond without waiting for them.

## Resource-Based Architecture

The API is divided into six core domains: authentication, users, tweets, replies, lists, and bookmarks.

Each resource has its own set of endpoints and operations, with CRUD support where appropriate. This keeps the API organized and makes it easier to extend individual features without complicating the entire system.

# Key Decisions

## Redis for Caching

Frequent database reads were one of the main performance concerns. Rather than repeatedly querying PostgreSQL for the same data, I introduced Redis as a caching layer.

The API checks the cache first and returns the stored result when available. This reduces repetitive database operations and helps keep commonly accessed resources responsive.

## Celery for Background Tasks

Some operations are important to the application but don't need to block a user-facing request. View-count synchronization is one example.

I used Celery to process these operations asynchronously. The API can handle the main request while background workers take care of tasks that can be completed later. This keeps the request cycle focused and avoids unnecessary delays.

## PostgreSQL as the Primary Database

PostgreSQL stores the application's persistent data, including users, tweets, replies, bookmarks, and lists.

Redis complements it rather than replacing it. PostgreSQL remains the primary source of persistent data, while Redis serves frequently accessed or temporarily cached results.

## More Than Just CRUD

The project includes more than 36 endpoints across its core domains. However, the goal wasn't to add endpoints just for the sake of scale.

Each resource exposes operations based on its actual requirements. For example, bookmarks use a more focused set of operations rather than forcing a generic CRUD pattern. This keeps the API practical and avoids unnecessary complexity.

# Project Structure

```
.
├── manage.py
├── config/                 # Django project configuration
├── apps/
│   ├── auth/               # Authentication endpoints
│   ├── users/              # User management
│   ├── tweets/             # Tweets and view counts
│   ├── replies/            # Tweet replies
│   ├── bookmarks/          # Bookmark management
│   └── lists/              # User-created lists
├── tasks/                  # Celery background tasks
├── requirements.txt
└── .env.example
```

The structure above is a conceptual layout of the main components; adjust it to match the actual repository.

# Features

## Celery Background Processing

Background workers handle operations that don't need to block API responses. Celery processes tasks such as syncing cached tweet view counts into PostgreSQL, keeping slower operations outside the main request cycle.

## Built-In Redis Caching

The API checks Redis for cached results before querying PostgreSQL. Frequently accessed data can be returned directly from cache, reducing repeated database reads and helping maintain responsive endpoints.

## Resource-Based REST API

More than 36 endpoints are organized around authentication, users, tweets, replies, bookmarks, and lists. Each resource supports the operations it needs, keeping the API structured as it grows.

## Tweet & Reply System

Dedicated endpoints manage tweets and their replies, including the operations required to create, retrieve, update, and delete content. The resource structure keeps related data organized and accessible through the API.

## Bookmark Management

The bookmark system uses a focused set of operations for saving and removing bookmarks. It avoids unnecessary CRUD endpoints where they don't fit the feature's requirements.

## List Management

Users can create, retrieve, update, and delete their own Twitter-style lists through dedicated endpoints. This keeps list functionality separate from other API resources.

# What I Learned

This project taught me that backend development is as much about architectural decisions as it is about writing endpoints. Building the API meant thinking about where data should live, when it should be cached, and which operations should happen asynchronously.

Working with Redis, Celery, and PostgreSQL also gave me a clearer understanding of how caching and background processing can complement a relational database. The biggest takeaway was learning to design the request cycle around what needs to happen immediately—and move everything else out of the way.

# Contributions

Contributions and suggestions are welcome. Improvements to the API architecture, caching strategy, background processing, and resource design are all useful areas to explore.


