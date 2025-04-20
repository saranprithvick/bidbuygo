# BidBuyGo - E-commerce Platform

BidBuyGo is a modern e-commerce platform that combines traditional shopping with auction features. It allows users to buy products directly or participate in auctions to get the best deals.

## Features

- User Authentication (Login/Register)
- Product Management
- Shopping Cart
- Order Processing
- Payment Integration (Razorpay)
- Auction System
- Admin Dashboard
- Responsive Design

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd djangoproject
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the project root with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
RAZORPAY_KEY_ID=your-razorpay-key
RAZORPAY_KEY_SECRET=your-razorpay-secret
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Media Folder Setup

The project uses a media folder to store uploaded files (product images, etc.). Here's how to set it up:

1. The media folder is located at `media/` in the project root
2. It contains subdirectories for different types of media:
   - `media/products/` - Stores product images
   - `media/profile_pics/` - Stores user profile pictures

3. To ensure proper functioning:
   - Make sure the media folder has write permissions
   - The folder structure is automatically created when needed
   - In development, Django will serve media files
   - In production, configure your web server to serve media files

4. Important notes:
   - Never commit the media folder to version control
   - Add `media/` to your `.gitignore` file
   - Back up media files regularly
   - In production, consider using a cloud storage service (AWS S3, etc.)

## Project Structure

```
djangoproject/
├── bidbuygo/              # Main application
│   ├── migrations/        # Database migrations
│   ├── templates/         # HTML templates
│   ├── static/           # Static files (CSS, JS, images)
│   ├── models.py         # Database models
│   ├── views.py          # View functions
│   ├── urls.py           # URL patterns
│   └── ...
├── media/                # Uploaded media files
├── static/              # Collected static files
├── manage.py            # Django management script
└── requirements.txt     # Project dependencies
```

## Running the Project

1. Start the development server:
```bash
python manage.py runserver
```

2. Access the application at:
- Main site: http://127.0.0.1:8000/
- Admin interface: http://127.0.0.1:8000/admin/

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please contact [your-email@example.com]
