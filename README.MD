## ⚙️ Installation

1.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, install manually: `pip install django psycopg2 pillow validate_email`)*

3.  **Edit .env**
    cp env.example .env

4.  **Run Migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    python manage.py createsuperuser
    username: admin
    email: admin@admin.com
    password: 123456
    ```

4.  **Run Development Server**
    ```bash
    python manage.py runserver
    ```

5.  **Access the App**
    *   Open browser at: `http://127.0.0.1:8000`
6.  **Monitor the CSV file**
    ```bash
    python manage.py import_csv logdata.csv
    ```
7. **Refresh the page**
    ```bash
    python manage.py flush
    ```