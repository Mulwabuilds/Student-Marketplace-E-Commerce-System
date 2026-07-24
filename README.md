# Student Marketplace E-Commerce System

A web-based marketplace that enables university students to buy and sell products and services within the campus community. The platform provides secure user authentication, product listing management, product search and filtering, and seller profile management.

## Features

- User registration and login
- Product listing management
- Product search and category filtering
- Seller profile management
- Responsive Bootstrap interface

## Technologies Used

- Python
- Django
- PostgreSQL
- Bootstrap 5
- HTML, CSS, JavaScript
- Git & GitHub

## Authors

- Kevin Mulwa
- Ian Githumbi
- Lee Kaburu

**Kabarak University**  
Bachelor of Computer Science Project


<details>
<summary><b>🛠️ Quick Setup & Local Installation</b></summary>

```bash
# 1. Clone the repository and navigate into the project folder
git clone https://github.com/Spectral-Kaburu/Student-Marketplace-E-Commerce-System.git
cd Student-Marketplace-E-Commerce-System/

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env

# 5. Run database migrations
python manage.py makemigrations
python manage.py migrate

# 6. Seed the database
python manage.py seed_categories
python manage.py seed_catalog
python manage.py seed_data
python manage.py seed_services
python manage.py seed_demo

# 7. Run the development server
python manage.py runserver```