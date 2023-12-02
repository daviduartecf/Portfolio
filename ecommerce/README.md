## Getting Started

To run this project locally, follow these steps:

1. **Clone the repository:**

    ```bash
    git clone https://github.com/daviduartecf/Portfolio.git
    cd Portfolio
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
4. **Install requirements:**

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
