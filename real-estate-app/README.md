Ահա նախագծի մանրամասն **`README.md`** ֆայլը անգլերեն լեզվով, որտեղ ներառված են ծրագրի տեղադրման, կարգավորման և գործարկման բոլոր քայլերը ինչպես ֆրոնտենդի, այնպես էլ բեքենդի համար։

```markdown
# Real Estate Price Analysis & ML System

A full-stack web application that integrates a React (Tailwind CSS) frontend with a Python (Flask) backend and Machine Learning models to analyze real estate listings and predict price increases based on added property features.

---

## Project Structure

```text
real-estate-app/
│
├── backend/                  # Backend & Machine Learning part
│   ├── app.py                # Flask main server and API endpoints
│   ├── model.py              # ML models logic (Linear Regression, Random Forest, XGBoost)
│   ├── requirements.txt      # Python dependencies
│   └── data/                 # Data folder
│       └── listings.csv      # Real estate dataset
│
├── frontend/                 # Web interface (React + Vite + Tailwind CSS)
│   ├── public/
│   │   └── index.html        # Main HTML file
│   ├── src/
│   │   ├── App.jsx           # Main React component
│   │   ├── main.jsx          # React entry point
│   │   └── index.css         # Tailwind styles
│   ├── package.json          # Node.js dependencies
│   └── tailwind.config.js    # Tailwind configuration
│
├── Dockerfile                # Docker containerization file
├── docker-compose.yml        # Docker Compose configuration
└── README.md                 # Project documentation

```

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Python** (version 3.8 or higher)
* **Node.js** (version 16 or higher) and **npm**
* **Git**

---

## Getting Started & Installation Steps

### Step 1. Clone the Repository and Navigate to Project

Open your terminal and clone or open your local project repository:

```bash
git clone [https://github.com/astghiksaghyan/real-estate-app.git](https://github.com/astghiksaghyan/real-estate-app.git)
cd real-estate-app

```

---

### Step 2. Set Up and Run the Backend

1. Navigate to the `backend` folder:
```bash
cd backend

```


2. Create and activate a virtual environment (recommended):
* **macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```


* **Windows:**
```bash
python -m venv venv
venv\Scripts\activate

```




3. Install the required Python dependencies:
```bash
pip install -r requirements.txt

```


4. Ensure your `listings.csv` file is placed inside the `backend/data/` folder.
5. Run the Flask server:
```bash
python app.py

```


*The backend will start running at `h
`.*

---

### Step 3. Set Up and Run the Frontend

1. Open a **new terminal window/tab**, and navigate to the `frontend` folder from the root directory:
```bash
cd frontend

```


2. Install the Node.js dependencies:
```bash
npm install

```
2. Generate tailwind.config.js and postcss.config.js

```bash
npx tailwindcss init -p

```



3. Start the development server (using Vite):
```bash
npm run dev

```


*Vite will typically output a local URL (e.g., `http://localhost:5173` or `http://localhost:3000`). Open it in your web browser.*

---

## Running with Podman Compose

If you prefer running the application containers using `podman-compose`:

1. Make sure **podman-compose** is installed in your environment.
2. From the root directory of the project, build the container images:
```bash
   podman-compose -f docker-compose.yml build

```

3. Start the application services in the background:

```bash
podman-compose -f docker-compose.yml up -d

```

---

## Usage Guide

1. Open the frontend web app in your browser.
2. Browse through the randomly loaded real estate listings fetched from the dataset.
3. Click on any property card to view its detailed parameters (location, price, rooms, area).
4. Select a missing feature/improvement (e.g., "Վերանորոգում", "Կահույք", etc.).
5. Click the **"Սկսել Վերլուծությունը"** (Start Analysis) button to trigger the machine learning models (Linear Regression, Random Forest, XGBoost).
6. View the predicted price increase, valuation metrics, and recommendations on the screen.



gcloud auth login