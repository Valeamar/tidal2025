# Farmer Budget Optimizer

AI-powered agricultural input price optimization system that helps farmers plan their growing season expenses by finding optimal prices for agricultural inputs.

## Project Structure

```
farmer-budget-optimizer/
├── frontend/                 # React TypeScript frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── types/
│   │   │   └── index.ts     # TypeScript interfaces
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   └── index.css
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI application
│   │   └── models.py        # Pydantic data models
│   ├── requirements.txt
│   ├── run.py              # Startup script
│   └── .env.example        # Environment configuration template
└── README.md
```

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment configuration:
   ```bash
   cp .env.example .env
   ```

5. Run the FastAPI server:
   ```bash
   python run.py
   ```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The React app will be available at `http://localhost:3000`.

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /api/health` - Health check endpoint
- `POST /api/analyze` - Product analysis endpoint (to be implemented)
- `GET /docs` - Interactive API documentation

## Core Interfaces

The system uses TypeScript interfaces for type safety across frontend and backend:

- `ProductInput` - Agricultural product specifications
- `FarmInfo` - Farm location and details
- `PriceAnalysis` - Price analysis results with recommendations
- `AnalyzeRequest/Response` - API request/response formats

## Requirements Addressed

This initial setup addresses requirements:
- **7.1**: Fast system response (< 5 minutes for analysis)
- **7.2**: Simple web interface with no installation required
- **7.3**: Quick loading interface (< 3 seconds)

## Next Steps

The project structure is now ready for implementing:
1. Data models and storage (Task 2)
2. Market data service (Task 3)
3. Price calculator (Task 4)
4. AWS BI integration (Task 5)
5. Analysis agent (Task 6)
6. API endpoints (Task 7)
7. Frontend components (Task 8)
8. AWS services integration (Task 9)
9. Testing and deployment (Task 10)