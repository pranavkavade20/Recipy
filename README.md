# 🍲 Recipy Web Application

## 🌟 Overview

The **Recipy Web Application** is a personalized and efficient platform designed to **streamline meal planning** and **recipe discovery** based on the ingredients users already have at home. It moves beyond traditional, time-consuming recipe browsing by intelligently suggesting meals. This functionality helps users **save time**, **reduce food waste**, and discover new culinary creations.

---

## ✨ Features

The application is built around a set of robust features to enhance the user experience:

* **Intelligent Ingredient Search**: Users can input the ingredients they have on hand, and the system suggests recipes that match, simplifying the daily challenge of deciding what to cook.
* **Personalized Recommendations**: A **machine learning** model, powered by **scikit-learn**, learns from user behavior, search history, and frequently used ingredients to deliver increasingly relevant and tailored recipe suggestions over time.
* **Comprehensive Recipe Database**: Access a wide collection of recipes with detailed instructions, ingredient lists, and **nutritional information**.
* **Advanced Search and Filtering**: A user-friendly interface allows for filtering recipes based on keywords, ingredients, dietary restrictions, and estimated cooking time.
* **User Account Management**: Users can create profiles, **save favorite recipes**, track their cooking history, and manage personal settings.
* **Community Contribution**: A platform where users can **contribute their own recipes**, fostering a sense of community and enriching the available database of dishes.
* **Interactive Cooking Guides**: Step-by-step instructions, visual aids, and timers to help streamline the preparation process.

---

## 💻 Tech Stack

| Component | Technologies |
| :--- | :--- |
| **Frontend** | **HTML5, CSS3, Tailwind CSS** (for styling and rapid development), **JavaScript** (for interactivity and DOM manipulation) |
| **Backend** | **Python (Django)** (Web Framework), **Django REST Framework (DRF)** (for API creation) |
| **Database** | **MySQL** |
| **Machine Learning** | **Python (scikit-learn)** (for recommendation engine development and deployment) |

---

## 🚀 Getting Started

To set up and run the project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [Your Repository URL]
    cd Recipy
    ```
2.  **Set up the Python environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```
3.  **Configure MySQL Database:**
    * Ensure you have a **MySQL** server running.
    * Create a database for the project (e.g., `recipy_db`).
    * Update the database settings in your Django configuration file (e.g., `settings.py`) with your MySQL credentials.
4.  **Run Migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
5.  **Run the Server:**
    ```bash
    python manage.py runserver
    ```
    The application will be accessible at `http://127.0.0.1:8000/`.

---

## 🎥 Project Demonstration

### Watch the Project in Action! (Google Drive Link)

Click the link below to view the full video demonstration of the **Recipy Web Application** hosted on Google Drive.

[**▶️ WATCH FULL DEMO VIDEO ON GOOGLE DRIVE**]([https://drive.google.com/file/d/1V2SJyqkgycLODRvdd4tYYzgDNGcB7tHx])

> **IMPORTANT:** Ensure your Google Drive video file is set to "Anyone with the link can view" to guarantee access for repository visitors. Replace `[YOUR_PUBLIC_GOOGLE_DRIVE_VIDEO_LINK]` with the shareable URL of your video.

---

## 🤝 Contribution

We welcome contributions from the community! If you'd like to improve the application, please refer to our `CONTRIBUTING.md` file for guidelines on submitting pull requests and reporting issues.

---

## 📄 License

*\[Insert License Information here, e.g., This project is licensed under the MIT License.]*
