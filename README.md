
# ✨ AI SolveXpert: Your Ultimate Math Problem Solver ✨

## 🚀 Project Overview

AI SolveXpert is an innovative Final Year Project (FYP) meticulously designed to revolutionize how students and educators approach complex mathematical problems. This platform stands out as a full context-based math problem solver, capable of understanding intricate queries and delivering precise, detailed solutions. Beyond basic problem-solving, SolveXpert integrates cutting-edge AI functionalities, including a robust document-based Question & Answer (Q\&A) system, dynamic AI interaction, and immersive audio-visual response mechanisms. The inclusion of a Retrieval-Augmented Generation (RAG) page, complete with seamless voice input and output capabilities, and an integrated, animated avatar, ensures an engaging, accessible, and highly interactive user experience.

## 🌟 Key Features

  * **Intelligent Math Problem Solving:**
      * Delivers step-by-step solutions for a wide range of mathematical problems, grasping the full context of the user's input.
      * Designed to handle complex equations, word problems, and theoretical questions.
  * **📚 Advanced RAG System:**
      * Empowers users to upload diverse documents (e.g., PDFs, textbooks, research papers).
      * Leverages a sophisticated Retrieval-Augmented Generation model to fetch and synthesize information from these documents, providing accurate and contextually relevant answers to user queries.
  * **🗣️ Seamless Voice Interaction:**
      * **Voice Input:** Users can pose questions verbally, making the platform accessible and convenient for hands-free operation.
      * **Voice Output:** Responses are generated and delivered audibly, offering an intuitive and natural interaction experience.
  * **🤖 Integrated Interactive Avatar:**
      * A dynamic, animated avatar enhances user engagement by visually presenting responses and feedback.
      * Adds a personal touch to the AI interaction, making the learning process more enjoyable.
  * **📄 Document-Based Q\&A:**
      * Go beyond simple search by allowing users to ask specific questions directly related to their uploaded content.
      * Ideal for studying, research, and quick information retrieval from large documents.
  * **User-Friendly Interface:**
      * An intuitive and clean design ensures ease of navigation and a smooth user journey from problem submission to solution retrieval.

## 🛠️ Technologies & Libraries

This project is built using a powerful stack of modern technologies and advanced AI libraries to ensure performance, scalability, and intelligence.

  * **Web Framework:**
      * **Django:** A high-level Python web framework that encourages rapid development and clean, pragmatic design. It provides a robust backend for handling user requests, data management, and AI model integration.
  * **Database Management:**
      * **MySQL:** A widely used open-source relational database management system. It serves as the backbone for storing user data, problem queries, solutions, and document embeddings.
      * **XAMPP Server:** Used for easy local development and management of the MySQL database.
  * **Artificial Intelligence & Machine Learning:**
      * **Finetuned Custom AI Model:** At the core of SolveXpert is a custom AI model that has been meticulously finetuned to excel in mathematical problem-solving and contextual understanding.
      * **Gemini Flash 2.0:** Leveraging Google's state-of-the-art large language model for advanced natural language processing, generation, and complex reasoning capabilities.
  * **Key Libraries & Tools:**
      * **LangChain:** A powerful framework designed for developing applications powered by language models. It facilitates the chaining of various components to build complex LLM workflows, crucial for the RAG system and overall AI orchestration.
      * **PyTesseract:** A Python wrapper for Google's Tesseract-OCR Engine, enabling the extraction of text from images within documents, vital for processing diverse input formats.
      * **Other Libraries:** A multitude of other Python libraries are utilized for tasks such as data processing, numerical computation, voice synthesis/recognition, and avatar animation.

## 🚀 Installation & Setup Guide

Follow these steps to get AI SolveXpert up and running on your local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

  * **Python 3.8+**: Download from [python.org](https://www.python.org/).
  * **pip**: Python package installer (comes with Python).
  * **XAMPP**: For MySQL database. Download from [apachefriends.org](https://www.apachefriends.org/).
  * **Tesseract OCR Engine**: PyTesseract requires the Tesseract executable. Installation instructions can be found on the [PyTesseract GitHub page](https://github.com/madmaze/pytesseract).

### Installation Steps

1.  **Clone the Repository:**
    Start by cloning the project repository from GitHub to your local machine.

    ```bash
    git clone https://github.com/HaseebUlHassan437/fyp-SolveXpert.git
    cd fyp-SolveXpert
    ```

2.  **Set Up Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.

    ```bash
    python -m venv venv
    ```

    Activate the virtual environment:

      * **Windows:**

        ```bash
        .\venv\Scripts\activate
        ```

      * **macOS/Linux:**

        ```bash
        source venv/bin/activate
        ```

3.  **Install Python Dependencies:**
    Install all required Python libraries using the `requirements.txt` file.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Configuration (MySQL with XAMPP):**

      * Start **Apache** and **MySQL** services from your XAMPP control panel.

      * Access `phpMyAdmin` (usually `http://localhost/phpmyadmin/`) through your browser.

      * Create a new database for SolveXpert (e.g., `solvexpert_db`).

      * Open the `fyp-SolveXpert/solvexpert/settings.py` file.

      * Locate the `DATABASES` setting and update it with your MySQL credentials, ensuring the `NAME` matches your created database name.

        ```python
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'solvexpert_db', # Your database name
                'USER': 'root',          # Your MySQL username
                'PASSWORD': '',          # Your MySQL password (leave empty if none)
                'HOST': 'localhost',
                'PORT': '3306',
            }
        }
        ```

      * Apply database migrations to create the necessary tables:

        ```bash
        python manage.py makemigrations
        python manage.py migrate
        ```

5.  **Run the Django Application:**
    Once all dependencies are installed and the database is configured, you can start the Django development server.

    ```bash
    python manage.py runserver
    ```

    The application will typically be accessible at `http://127.0.0.1:8000/` in your web browser.

## 🖥️ How to Use AI SolveXpert

Upon launching the application, you'll be greeted with a user-friendly interface designed for seamless interaction.

1.  **User Registration & Login:**
      * New users must first register with a valid email and password.
      * After successful registration (and email verification, if implemented), users can log in to access the main dashboard.
2.  **Solver Page:**
      * Navigate to the "Solver" page.
      * Input your mathematical problem in the provided text area.
      * Submit the problem, and AI SolveXpert will process it to provide a detailed, context-aware solution.
3.  **RAG Page (Retrieval-Augmented Generation):**
      * Access the "RAG" page.
      * **Upload Documents:** Use the upload feature to provide study materials, textbooks, or any relevant documents.
      * **Ask Questions:** Type or use voice input to ask questions related to the content of your uploaded documents.
      * **Receive Responses:** The system will generate accurate answers, presented both visually and audibly via the integrated avatar.
4.  **Voice Interaction:**
      * Look for microphone icons or voice input prompts.
      * Speak your queries clearly into your microphone.
      * Listen to the AI's responses, which will be articulated through the platform's voice output system.
5.  **Interactive Avatar:**
      * The animated avatar will accompany the AI's responses, providing visual cues and enhancing the overall interactive experience.

## 📂 Project Structure (Typical)

A high-level overview of the project's directory structure:

```
fyp-SolveXpert/
├── solvexpert/                 # Django project settings and main URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                       # Core application (e.g., common functionalities)
├── users/                      # User authentication and profile management
├── solver/                     # Application for math problem solving logic
├── rag/                        # Application for RAG system and document processing
├── media/                      # User-uploaded files (e.g., documents for RAG)
├── static/                     # Static files (CSS, JS, images)
├── templates/                  # HTML templates for rendering pages
├── venv/                       # Python virtual environment
├── manage.py                   # Django's command-line utility
└── requirements.txt            # List of Python dependencies
```

## 📈 Future Enhancements

Potential areas for future development and expansion of AI SolveXpert:

  * **Broader Subject Support:** Extend the problem-solving capabilities beyond mathematics to physics, chemistry, or other STEM fields.
  * **Handwritten Input Recognition:** Implement advanced OCR and NLP for solving problems from handwritten notes or images.
  * **Multi-language Support:** Enable the platform to understand and respond in multiple languages.
  * **Interactive Graphing Tools:** Integrate dynamic plotting tools to visualize mathematical functions and data.
  * **Personalized Learning Paths:** Develop features for tracking user progress and suggesting tailored learning materials.
  * **Community Features:** Introduce forums or collaborative spaces for users to discuss problems and solutions.

## 📽️ Project Video Demonstration

This video provides a demonstration of the AI SolveXpert platform and its features.

The video showcases the following functionalities:

  * **Secure Login and Sign-up:** Users can securely log in or sign up using their email addresses.
  * **Math Problem Solving:** The AI model can solve math questions typed by the user or extracted from uploaded images using OCR.
  * **Document-Based Question Answering (RAG):** Users can upload documents and ask context-based questions.
  * **Spoken Answers with Avatar:** A Chroma Avatar provides spoken answers using text-to-speech.
  * **Chat History and Context:** The platform maintains chat history for continuous learning.
  * **Separate Pages:** The platform has distinct pages for model-based solving and document-based solving.
  * **Light and Dark Theme:** The platform supports both light and dark themes.

## 🔗 Project Links

  * **GitHub Repository:** [HaseebUlHassan437/fyp-SolveXpert](https://github.com/HaseebUlHassan437/fyp-SolveXpert/tree/main)
  * **Final Year Project Report:** [SolveXpertFinalReport.pdf](SolveXpertFinalReport.pdf)
  * **Project Video:** [AI SolveXpert Demonstration](https://www.youtube.com/watch?v=wtenLqpVXoQ&t=1s)

-----
