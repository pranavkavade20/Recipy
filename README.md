<div align="center">
  <h1 align="center">Recipy</h1>
  <p align="center">
    An intelligent meal planning and recipe discovery platform powered by Machine Learning.
    <br />
    <a href="https://drive.google.com/file/d/11ir8zZiosqaJmlcg60Uft2iT2djzGUlA/preview"><strong>View Demo Video »</strong></a>
  </p>
</div>

<!-- Badges -->
<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/Scikit_Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-Learn" />
  <img src="https://img.shields.io/badge/Numpy-777BB4?style=for-the-badge&logo=numpy&logoColor=white" alt="NumPy" />
  <img src="https://img.shields.io/badge/Pandas-2C2D72?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <br/>
  <br/>
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5" />
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="TailwindCSS" />
  <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" />
</div>

<br />

## 📖 About The Project

The **Recipy** is a personalized and efficient platform designed to **streamline meal planning** and **recipe discovery** based on the ingredients you already have at home. It moves beyond traditional, time-consuming recipe browsing by intelligently suggesting meals that match your available ingredients. 

This functionality helps users **save time**, **reduce food waste**, and effortlessly discover new culinary creations.


## ✨ Key Features

* 🔍 **Intelligent Ingredient Search**: Input your available ingredients to instantly discover matching recipes, taking the guesswork out of daily meal prep.
* 🤖 **Personalized Recommendations**: A recommendation engine powered by **scikit-learn** learns from your search history and frequently used ingredients to deliver highly tailored meal suggestions.
* 📚 **Comprehensive Recipe Database**: Access an extensive, growing collection of recipes complete with detailed instructions, ingredient lists, and nutritional information.
* ⚙️ **Advanced Filtering**: Quickly refine search results based on keywords, ingredients, dietary restrictions, and cooking time.
* 👤 **User Accounts & Bookmarks**: Create a personalized profile, save favorite meals, track your culinary journeys, and manage your preferences seamlessly.
* 🤝 **Community Contribution**: Add your own signature dishes to the Recipy database, fostering a community-driven catalog of culinary inspiration.
* 📺 **Integrated Cooking Guides**: Access embedded visual guides and step-by-step instructions to streamline the cooking process.


## 🛠 Tech Stack

| Domain | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, **Tailwind CSS**, JavaScript |
| **Backend** | **Python**, **Django**, Django REST Framework (DRF) |
| **Database** | **MySQL** |
| **Machine Learning** | **Python** (scikit-learn, Numpy, Pandas, Faiss) |


## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

Ensure you have the following installed on your local machine:
* Python 3.10+
* Node.js & npm (for Tailwind CSS framework)
* MySQL Server

### 1. Clone the repository
```bash
git clone https://github.com/pranavkavade20/Recipy.git
cd Recipy
```

### 2. Set up a Python Virtual Environment
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```
**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
1. Duplicate the `.env.example` file and rename it to `.env`.
2. Open the `.env` file and insert your local configuration:

```env
# YouTube API key for video fetching
YOUTUBE_API_KEY="your_youtube_api_key"

# Django Secret Key
SECRET_KEY="your_django_secret_key"

# Database Credentials
DATABASE_NAME="recipy_db"
DATABASE_PASSWORD="your_mysql_password"
DATABASE_USER="root" # Optional (Defaults to root)
```

### 5. Configure MySQL Database
* Ensure your MySQL server service is running locally.
* Create a database matching the `DATABASE_NAME` in your `.env`:
  ```sql
  CREATE DATABASE recipy_db;
  ```

### 6. Run Database Migrations
Create the core database schema and apply necessary model changes:
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Install and Build Tailwind CSS
Since the project uses `django-tailwind`, you must install the Node dependencies inside the `theme` app:
```bash
python manage.py tailwind install
```

To compile your Tailwind classes and start the watch process (run this in a separate terminal during development):
```bash
python manage.py tailwind start
```

### 8. Start the Development Server
```bash
python manage.py runserver
```
*The application should now be securely running at `http://127.0.0.1:8000/`*


## 📂 Project Structure

```text
Recipy/
├── RecipeAssistant/       # Main Django project settings and root configurations
├── recipes/               # Recipe management, search mechanisms, and ML logic
├── users/                 # Custom authentication, user profiles, history, and bookmarks
├── theme/                 # Tailwind CSS configuration, NPM dependencies, and build pipeline
├── static/                # Global static files (images, custom js)
├── templates/             # Global standard HTML templates
├── media/                 # User-uploaded content
├── requirements.txt       # Python dependencies configuration
└── manage.py              # Django CLI utility
```


## 🎥 Demo

Experience Recipy in action:
* [▶️ Full Video Demonstration (Google Drive)](https://drive.google.com/file/d/11ir8zZiosqaJmlcg60Uft2iT2djzGUlA/preview)

---

<p align="center">
  Built with ❤️ for hassle-free cooking.
</p>
