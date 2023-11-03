# Tour Review AI Documentation

The Tour Review AI project serves as a sophisticated aggregator of customer reviews, meticulously crafted with the aim of harvesting testimonials from a broad array of booking and social media platforms. Designed as a reliable resource, this tool fetches data from an extensive list of platforms, including but not limited to:

- Airbnb
- Civitatis
- Expedia
- Klook
- Get Your Guide
- TripAdvisor
- Viator
- Facebook
- Instagram
- Google

## Technical Architecture and Stack

This comprehensive project leverages the robust capabilities of the Django REST Framework for its backend operations, while employing Angular for a sleek and responsive frontend interface.

### Data Retrieval Mechanism

The core engine that powers the data harvesting process is quite conventional yet effective. The backend, developed using Django, exposes a set of API endpoints. These are subsequently polled by the Angular-based frontend to fetch the requisite data.

### Hosting and Containerization

Both the frontend and backend components are co-located on a single Amazon EC2 server for streamlined operations. They are containerized using Docker Compose and have an nginx layer to manage the exposure of their respective ports.

- Backend on Port 8000
- Frontend on Port 80

### Frontend Architecture

The frontend deploys a rather standard but efficient setup. Angular runs within its designated Docker Compose bucket, and nginx serves the application to the outside world on port 80.

### Backend Ecosystem

The backend is a composite of multiple services each performing a specialized role:

- **Django Backend**: The core application itself, responsible for data management and API exposure.
  
- **Nginx Proxy**: This service acts as the gatekeeper, allowing the Django backend to be accessible externally via port 8000.

- **Redis**: Employed as an in-memory data store.

- **Celery**: Task queue to handle asynchronous jobs.
  
- **Celery Beat**: A scheduler for Celery tasks.

Additionally, the system integrates a Selenium Grid service for heavy computational tasks, which is deployed on a separate, more powerful server to meet resource-intensive requirements.

### Security Measures

To ensure the utmost security, sensitive variables are stored in a `.env` file that is intentionally kept out of the version control system. A template for this `.env` file is available below the platform description for reference.

____

### Django Backend
The Django backend is composed by four applications.

**API:**
\
This application acts as the pivotal integration layer that bridges the gap between the backend data storage and the frontend user interface. Through its meticulously designed architecture, the application ensures that data flows smoothly and coherently across these two facets. This is primarily facilitated by the `views` directory, which serves as the heart of the operation.

### Role of the `views` Directory:

1. **Central Repository of View Functions**: 
    - Nestled within the `views` directory is an extensive collection of view functions that play critical roles in data manipulation and retrieval. 
    - These functions act as the core conduits through which the backend communicates with the frontend, transforming stored data into consumable, structured formats.

2. **Data Processing and Delivery**:
    - Besides just serving as a mechanism for data retrieval, these view functions often include business logic to manipulate and adapt the data according to specific requirements.
    - Once processed, the data is made available to the frontend via a well-defined Application Programming Interface (API).

### Additional Financial Management Capabilities:

While the core focus of the `views` directory is data management, it also wears a second hat: financial transaction management.

1. **Unified Payment Gateway Interface**: 
    - The `views` directory includes specialized files responsible for interfacing with both PayPal and Stripe.
    - This multi-platform approach ensures a versatile and flexible payment system, offering users the convenience of selecting their preferred payment method.

2. **Comprehensive Payment Management**:
    - Beyond merely facilitating payments, these view functions are intricately designed to handle a variety of related tasks.
    - These include subscription management, payment verification, transaction logging, and even automated invoicing, all orchestrated through the API.

In summary, the application is not just a data router but a multifaceted solution. While its primary role is to serve as a reliable intermediary for data exchange between the frontend and the backend, it also efficiently manages financial transactions, making it a holistic solution for the organization's operational needs.

____

## Focus on payments
### PayPal Functions and Classes:

1. **`paypal_config` Function:**
   - This function serves as an endpoint to handle incoming HTTP GET requests.
   - When triggered, it accesses the Django settings to fetch PayPal's client ID and client secret.
   - Afterward, it returns these credentials as part of a JSON response to the client.
   - The function is also marked as CSRF-exempt, meaning it is explicitly designed to not require a CSRF token, a security measure commonly used in Django web applications.

2. **`CreateCheckoutSessionView` Class:**
   - This is a class-based view that listens specifically for POST requests.
   - Inside the method, it uses a serializer to validate the data present in the incoming request.
   - Depending on the specified plan (SMALL, MEDIUM, or LARGE), it calculates the appropriate price, generates a PayPal access token, and attempts to establish a new subscription.
   - A new Payment object with a status set to "Pending" is then created in the database.
   - Finally, it returns a JSON response that includes the PayPal session ID and the URL where the payment can be completed.

### Stripe Functions and Classes:

1. **`stripe_config` Function:**
   - Similar to its PayPal counterpart, this function handles HTTP GET requests.
   - It responds with a JSON object containing Stripe's public key.
   - CSRF protection is disabled for this function, making it easier to integrate with third-party services that may not support CSRF tokens.

2. **`CreateCheckoutSessionView` Class:**
   - Listens for POST HTTP requests.
   - Based on the incoming request data, it determines which payment plan the user has chosen and initializes a Stripe checkout session.
   - The method then returns a JSON response containing the session ID and the URL where the payment process can be completed.

3. **`DeleteSubscriptionView` Class:**
   - This class listens for POST HTTP requests to cancel a subscription.
   - It supports cancellation for both Stripe and PayPal and works by finding the associated company based on the user’s details.
   - Upon successful cancellation, a JSON response confirming the action is returned to the client.

4. **`UpgradeSubscriptionView` Class:**
   - Designed to handle POST requests to upgrade an existing Stripe subscription to a new plan.
   - It modifies the current Stripe subscription to reflect the new plan chosen by the user and updates the related company records accordingly.
   - The method then sends back a JSON response to confirm the subscription upgrade.

### Webhook Handlers:

1. **`stripe_webhook` Function:**
   - This function serves as the webhook endpoint for Stripe.
   - It listens for specific events, namely the completion of a checkout session, and performs corresponding updates in the database.
   - After successfully handling the event, it returns an HTTP 200 status code.

2. **`paypal_webhook` Function:**
   - This is the webhook endpoint for PayPal.
   - The function listens for the event type "BILLING.SUBSCRIPTION.ACTIVATED" to trigger its logic.
   - It verifies the received event for authenticity before proceeding to update related records in the database.
   - Like the Stripe webhook, it returns an HTTP 200 status code upon successful execution but also handles errors gracefully with appropriate HTTP status codes.

This structure ensures that your web application can efficiently handle both Stripe and PayPal for payment operations while maintaining a consistent and secure workflow.

**AUTHENTICATION:**
\
This application is the dedicated platform responsible for 
handling all authentication operations required to maintain 
data security and reliability for the frontend. It provides a 
suite of features including user login, password reset, role management, 
and employee account creation.

**TOUR REVIEW AI:**
\
Serving as the backbone of the entire software ecosystem, this Core Application is pivotal for orchestrating basic to advanced settings that govern how the application operates. The architecture of this core module is meticulously designed to allow seamless configuration, making it indispensable for overall system functionality.

One of the cornerstone files within this application is `tasks.py`. 

here's a breakdown of some of the core functions in the `tasks.py`:

1. **`run_background_scrapers`**: This is the main function that orchestrates the scraping of various platforms. For each platform (e.g., Airbnb, Expedia), it filters records based on active user subscriptions and initiates scrapers by calling the `scrape` function asynchronously.

2. **`task_analise_reviews`**: A wrapper function for `analise_reviews`. It calls `analise_reviews` and handles exceptions. Primarily for making the `analise_reviews` function compatible with asynchronous tasks.

3. **`analise_reviews`**: This function fetches reviews that haven't been analyzed and uses OpenAI's API to obtain sentiment scores, country codes, cities, and other metadata. The results are updated in the corresponding database records.

4. **`create_prompt`**: A utility function that generates a prompt string for OpenAI's GPT engine. It takes in `product` and `review` as parameters to create a context for the GPT model to analyze.

5. **`task_schedule_email_report`**: This function generates and sends email reports. It fetches an `ExportSchedule` object based on an ID and accordingly sets the date range for the report. The function supports multiple formats like PDF and XLSX and emails the generated report.

6. **`get_text_from_id`**: A helper function that takes an ID for a search factor and returns the corresponding text description.

7. **`save_tmp_file` and `save_tmp_file_xlsx`**: These are utility functions that save data (likely report data) to temporary files. They are used to prepare the file before it is sent as an email attachment.

8. **`scrape`**: A generic scraping function that takes an `instance_id` and `type` as parameters. Based on these, it retrieves the relevant URL or credential stream and initializes the scraper. It updates the `status` of the stream and carries out the actual scraping through a bot imported dynamically.


Each of these functions serves a specific role within the larger process of scraping, analyzing, and reporting reviews. They make the script modular and each can be understood or modified without affecting the others significantly.
**STREAMS:**
\
The architecture of this application serves as the backbone for the organization's web scraping initiatives, offering a well-structured, automated, and versatile solution for data retrieval from a multitude of platforms. The application is primarily divided into two pivotal directories: `apis` and `scrapers`.

### Directory Structure:

1. **`apis` Folder:**
   - This directory houses scripts that facilitate data collection via official APIs of platforms like Facebook, Twitter, and so on.
   - The advantages of using APIs include reliability, speed, and legitimacy. As these APIs are officially provided by the platforms themselves, this method of data collection adheres to standard protocols and is usually straightforward to implement.
   - The scripts in this folder often involve making authenticated API calls to fetch the data streams, which are then processed and stored.

2. **`scrapers` Folder:**
   - This folder holds the machinery for more complex data retrieval tasks, particularly for websites or platforms that do not offer public APIs, like TripAdvisor.
   - One of the cornerstone files in this directory is `main_bot.py`, which serves as the orchestrator for various scraping tasks.

### `main_bot.py` Key Features:

1. **Selenium Grid Initialization**: 
   - The script kickstarts Selenium Grid sessions, a functionality that enables browser automation on multiple machines concurrently. This is crucial for scraping websites that demand intricate user interactions, which can't be mimicked by straightforward API calls.

2. **Session Management**: 
   - Beyond just firing up these Selenium sessions, `main_bot.py` oversees their entire lifecycle. This ensures optimal resource utilization by making sure each session is terminated once its designated task is accomplished.

3. **Proxy Rotation Integration**: 
   - One sophisticated aspect of `main_bot.py` is its proxy rotation feature. The script intermittently changes the proxy servers through which requests are sent, thereby disguising the scraping activities. This minimizes the likelihood of the scraper being identified and subsequently blocked by target platforms.

### Scraper Workflow:

1. **Scrape Function Initiation**: The workflow starts with the invocation of the `scrape()` function in the `tasks.py` file. This function initializes an instance of the `Bot()` class.
  
2. **Bot Activation**: This instance triggers the execution of specific scraping scripts, such as `bot.py` for scraping TripAdvisor data.

3. **Selenium Grid Session**: Inside `bot.py`, the `super().__init__(__file__)` function is called to establish a Selenium Grid session on the server.

4. **Task Commencement**: The script then invokes `self.start()` to commence the scraping operations.

5. **Data Extraction**: The actual data scraping is conducted based on instructions specified in the scraper script.

6. **Database Storage**: Upon successful data retrieval, the information is stored in the database.

7. **Session Termination**: Finally, `bot.py` calls the `self.close(self.results)` function to gracefully terminate the Selenium Grid session.

8. **API Exposure**: The scraped data is then made available through a Django-based API application for further consumption.

In summary, this dual-directory structure (`apis` and `scrapers`) equips the application with remarkable adaptability. While the `apis` folder accommodates a more "by-the-book" data collection approach through official APIs, the `scrapers` directory, helmed by `main_bot.py`, tackles more complex scraping scenarios requiring web interactions. This strategic division allows the application to be a one-stop solution for a wide range of web scraping needs.


Streams id:

VIATOR = 1
AIRBNB = 2
TRIPADVISOR = 3
EXPEDIA = 4
KLOOK = 5
CIVITAS = 6
GETYOURGUIDE = 7
FACEBOOK = 8
GOOGLE = 9
INSTAGRAM = 10
LINKEDIN = 11

The scraping mechanism queue has a max concurrency value.
Right now this value is set to 5, as we are currently using up to 5 rotating proxy for this project, but it can be changed in a higher or lower number.

>Our Selenium grid server, right now can host up to 12 simultaneous session.

This value can be changed in the `docker-compose.yaml` file, in the celery command where you see `--concurrency=5`

```yaml
    command: celery -A tour_reviews_ai worker --concurrency=5 --prefetch-multiplier=1 -l info
```


## Models (Database schema)
### List of Models Present:

1. `User` (imported from `authentication.models` and also defined in your code)
2. `Company` (imported from `authentication.models` and also defined in your code)
3. `StandardCopyEmailAddress`
4. `Review`
5. `Agency`
6. `Country`
7. `City`
8. `Tour`
9. `Stream` (abstract model)
10. `UrlStream`
11. `CredentialStream`
12. `ApiKeyStream`
13. `ScheduleEmailAddress`
14. `ExportSchedule`
15. `Notification`
16. `Payment`


### How the Models are Linked:
### User Model

1. **StandardCopyEmailAddress**: Stores email addresses for standard copies. Linked via a Foreign Key to `User`, indicating the owning user.
2. **Review**: Holds user reviews. Has a Foreign Key to `User` under the field `client`, specifying which user created the review.
3. **Agency**: Represents agencies and has a Foreign Key to `User`, specifying which user owns or is associated with the agency.
4. **Stream**: An abstract model that contains a Foreign Key to `User`, setting the base for several types of streams.
    - **UrlStream**: Inherits from `Stream`, and specializes in URL-based streams.
    - **CredentialStream**: Inherits from `Stream`, focusing on streams that require credentials.
    - **ApiKeyStream**: Inherits from `Stream`, and is used for streams that require API keys.
5. **ScheduleEmailAddress**: Contains email addresses for schedules. Has a Foreign Key to `User` under the field `client`.
6. **ExportSchedule**: Represents export schedules and has a Foreign Key to `User`, specifying which user the schedule belongs to.
7. **Notification**: Manages notifications and has two Foreign Keys to `User` - one indicating the user and another for the client_field.
8. **Payment**: Holds payment information. Linked to `Company`, which has a ManyToMany relationship with `User` via `related_users`.
9. **Tour**: Represents tours and has a Foreign Key to `User` under the field `client`, specifying the client responsible for the tour.

### Company Model

1. **Payment**: Manages company payments and is linked to `Company` via a Foreign Key.
2. **User**: There is a ManyToMany relationship between `Company` and `User` via the `related_users` field, showing which users are related to which companies.

### Geographical Models

1. **Review**: 
    - Has a Foreign Key to `Country`, representing the country associated with the review.
    - Has a Foreign Key to `City`, representing the city associated with the review.
    - Has a Foreign Key to `Tour`, indicating which tour the review is about.
    
2. **City**: 
    - Is linked to `Country` via a Foreign Key, indicating the country where the city is located.

### Abstract Models

1. **Stream**: An abstract model that serves as a base for `UrlStream`, `CredentialStream`, and `ApiKeyStream`.

### Hierarchical Models

- `Stream`: Parent abstract model
    - **UrlStream**: Inherits fields from `Stream` and specializes in URL-based streams.
    - **CredentialStream**: Inherits from `Stream` and specializes in credential-based streams.
    - **ApiKeyStream**: Inherits from `Stream` and specializes in API key-based streams.

____

## Developing

If you are trying to improve or debug the system, you can run celery on your local computer with the following commands:

```commandline
kill -9 $(ps aux | grep celery | grep -v grep | awk '{print $2}' | tr '\n'  ' ') > /dev/null 2>&1
celery -A tour_reviews_ai worker --concurrency=2 --prefetch-multiplier=1 -l info
celery -A tour_reviews_ai beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```


### Installation

If you need to deploy a new version of the system you need to use the following commands.


Run the docker:
```commandline
docker-compose -f docker/docker-compose.yaml -p TourReviewsAI up -d --build
```

Enter in the docker shell:
```commandline
 docker exec -it tourreviewsai_backend_1 /bin/sh
```

Run the migrations:
```commandline
python3 manage.py migrate
python3 manage.py collectstatic
```

Create a superuser
```commandline
python3 manage.py createsuperuser
```

If you need to debug bots, you can easily run a test one with the following command in the django shell:
``` Debug bots
from streams.scrapers.utilities import import_bot
from api.models import UrlStream
from django.shortcuts import get_object_or_404
from api.utils import get_streams

instance_id=13
instance = get_object_or_404(UrlStream, id=instance_id)
stream_name = get_streams(instance.source_stream)
Bot = import_bot(stream_name)
bot = Bot(instance, True)
```


### Template for the `.env` file:

```
ENV_NAME=local
DEBUG=True
PRODUCTION=False
DATABASE_URL=sqlite:///stt/db.sqlite3
ALLOWED_HOSTS=*
CORS_ORIGIN_WHITELIST=*
SQL_ENGINE=django.db.backends.mysql

#SECRET_KEY='somesecretkey'
MYSQL_DATABASE=TourReviewsAI
MYSQL_USER=TourReviewsAI
MYSQL_PASSWORD=TourReviewsAI
MYSQL_ROOT_PASSWORD=TourReviewsAI
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307
MYSQL_CHARSET=utf8mb4
MYSQL_COLLATION=utf8mb4_unicode_ci

EMAIL_HOST_USER=noreply@tourreview.com
EMAIL_HOST_PASSWORD=*********



OPENAI_API_KEY=*********



SELENIUM_GRID_HOST=16.170.222.97



STRIPE_PUBLISHABLE_KEY=pk_test_*********
STRIPE_SECRET_KEY=sk_test_*********
STRIPE_ENDPOINT_SECRET=whsec_*********

STRIPE_SUCCESS_URL=http://localhost:8000/v1/api/success?session_id={CHECKOUT_SESSION_ID}
STRIPE_CANCEL_URL=http://localhost:8000/v1/api/cancelled/


STRIPE_SMALL_PRICE_ID=price_*********
STRIPE_MEDIUM_PRICE_ID=price_*********
STRIPE_LARGE_PRICE_ID=price_*********



PAYPAL_CLIENT_ID=*********
PAYPAL_CLIENT_SECRET=*********
PAYPAL_WEBHOOK_ID=*********

PAYPAL_SMALL_PRICE_ID=*********
PAYPAL_MEDIUM_PRICE_ID=*********
PAYPAL_LARGE_PRICE_ID=*********
```
