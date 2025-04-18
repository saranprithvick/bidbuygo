# BidBuyGo E-commerce Platform

A Django-based e-commerce platform with bidding functionality.

## Quick Start

1. Clone the repository and navigate to the project directory
2. Create and activate a virtual environment
3. Install dependencies
4. Run migrations
5. Start the development server

That's it! The project uses SQLite by default, so no additional database setup is required.

## Detailed Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd djangoproject
```

### Step 2: Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Initialize the Database
```bash
# Create database tables
python manage.py migrate

# Create a superuser (optional, for admin access)
python manage.py createsuperuser
```

### Step 5: Populate Sample Data (Optional)
```bash
# Add sample products to the database
python manage.py populate_products
```

### Step 6: Run the Development Server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser to see the application running!

## Common Tasks

### Creating a New User
1. Visit http://127.0.0.1:8000/register/
2. Fill in the registration form
3. Log in with your credentials

### Accessing the Admin Interface
1. Visit http://127.0.0.1:8000/admin/
2. Log in with your superuser credentials

### Managing Products
- View products: http://127.0.0.1:8000/products/
- Add new products: http://127.0.0.1:8000/admin/bidbuygo/product/add/

## Features
- User authentication (login/register)
- Product listing and detail pages
- Bidding functionality
- Product management
- Image uploads

## Project Structure
- `mysite/` - Main project configuration
- `bidbuygo/` - Main application
- `templates/` - HTML templates
- `static/` - Static files (CSS, JS, images)
- `media/` - User-uploaded files
- `db.sqlite3` - Database file (created automatically)

## Troubleshooting

### If you see a "No module named" error
Make sure you've activated your virtual environment and installed all requirements:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### If the server won't start
Check if another process is using port 8000:
```bash
# On macOS/Linux
lsof -i :8000
# On Windows
netstat -ano | findstr :8000
```

### If you need to reset the database
```bash
# Delete the existing database
rm db.sqlite3
# Recreate the database
python manage.py migrate
python manage.py populate_products
```
