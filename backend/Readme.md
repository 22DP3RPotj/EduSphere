## Backend (Django)
The backend is built using **Django** and **Django Channels** to support real-time features like chat and notifications.

### Features
- User authentication (JWT-based with OAuth2 support)
- Course management (CRUD operations for courses)
- Payment processing (Stripe/PayPal)
- WebSockets for real-time messaging
- Role-based access control (Creator, Learner, Admin)
- PostgreSQL database with Redis for real-time operations

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-repo/course-marketplace.git
   cd course-marketplace/backend
   ```
2. **Create and activate a virtual environment:**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
4. **Set up environment variables:**
   Create a `.env` file in the root of the backend directory and add the following:
   ```sh
   SECRET_KEY=your_secret_key
   DEBUG=True
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=localhost
   DB_PORT=5432
   ```
5. **Run migrations:**
   ```sh
   python manage.py migrate
   ```
6. **Create a superuser (for admin access):**
   ```sh
   python manage.py createsuperuser
   ```
7. **Run the server:**
   ```sh
   python manage.py runserver
   ```
