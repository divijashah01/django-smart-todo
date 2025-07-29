# DoIt - A Smart To-Do & Planner Web App

[Python]
[Django]
[JavaScript]

DoIt is an intelligent web application designed to streamline task management. It combines traditional subject-based to-do lists and a daily planner with modern features like an AI-powered voice command interface and a comprehensive analytics dashboard to help users stay organized and productive.

---

## ✨ Key Features

- User Authentication**: Secure user registration and login system.
- **Subject-Based Task Management**: Organize tasks into color-coded subjects for better clarity and focus.
- **Calendar & Daily Planner**: A dedicated calendar view to manage tasks on a daily, weekly, and monthly basis, with support for repeating tasks.
- **AI-Powered Audio Task Creation**:
  - A standout feature that allows users to create tasks using voice commands.
  - Utilizes **OpenAI's Whisper** for highly accurate speech-to-text transcription.
  - Features **Smart Parsing** logic to automatically extract the task title, subject, due date, and time from natural language commands (e.g., *"Submit report for subject Marketing due tomorrow at 5 pm"*).
- **Advanced Analytics Dashboard**:
  - **Streaks**: Tracks current and longest daily task completion streaks to build user habits.
  - **Subject Performance**: Visual progress bars showing completion rates for each subject.
  - **Weekly Productivity Chart**: A dynamic bar chart (using Chart.js) visualizing task distribution across the days of the week.
  - **Key Metrics**: At-a-glance stats for overdue tasks and more.

---

## 🛠️ Tech Stack

- **Backend**: Python, Django
- **Frontend**: HTML5, CSS3, Vanilla JavaScript, Chart.js
- **Database**: SQLite3 (default)
- **AI/ML**: OpenAI Whisper for Speech-to-Text
- **Libraries**: `python-dateutil` for natural language date parsing

---

## 🚀 Local Setup and Installation

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/django-smart-todo.git](https://github.com/your-username/django-smart-todo.git)
    cd django-smart-todo
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install project dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Install FFmpeg:**
    The audio processing feature requires FFmpeg. Please install it on your system.
    - **macOS (with Homebrew):** `brew install ffmpeg`
    - **Linux (Debian/Ubuntu):** `sudo apt update && sudo apt install ffmpeg`
    - **Windows:** Download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add the `bin` folder to your system's PATH.

5.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`.
