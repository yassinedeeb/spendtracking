# Receipt Tracker

This is a simple spend tracking application that allows you to upload receipts, parse them using the Gemini API, and track your monthly spending.

## Setup

### Backend

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: A `requirements.txt` file will be generated in a later step)*

3.  **Create an environment file:**
    Create a file named `.env` in the `backend` directory and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_api_key_here
    ```

### Frontend

1.  **Navigate to the frontend directory:**
    ```bash
    cd frontend
    ```

2.  **Install the required Node.js packages:**
    ```bash
    npm install
    ```

## Running the Application

1.  **Start the backend server:**
    From the `backend` directory, run:
    ```bash
    python app.py
    ```

2.  **Start the frontend server:**
    From the `frontend` directory, run:
    ```bash
    npm start
    ```

The application will be available at `http://localhost:3000`.
