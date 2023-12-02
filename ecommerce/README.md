Your Project Name
Brief project description and purpose.

Prerequisites
List any software, tools, or dependencies users need to have installed on their machines before running your project. For example:

Python 3.x
Django 3.x
Other dependencies...
Getting Started
Provide step-by-step instructions on how to set up and run your project locally.

## Getting Started

To run this project locally, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/daviduartecf/ecommerce.git
    cd ecommerce
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment:**

    - On Windows:

        ```bash
        .\venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

4. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Run migrations:**

    ```bash
    python manage.py migrate
    ```

6. **Create a superuser (optional):**

    ```bash
    python manage.py createsuperuser
    ```

7. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

8. Open your browser and go to [http://localhost:8000/](http://localhost:8000/) to see the app.
