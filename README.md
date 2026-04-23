# SmartSheet — AI Dashboard Builder

SmartSheet transforms your spreadsheets into actionable insights using AI, helping you understand your data, discover patterns, and make better decisions faster.

Upload a `.csv` or `.xlsx` file, and the application will use **Google Gemini** to analyze your data, suggest impactful visualizations, and help you build an interactive dashboard within seconds.

---

## 🏗️ Architecture

```
smartsheet/
├── api/                          # Python FastAPI microservice
│   ├── app/
│   │   ├── config.py             # Settings via pydantic-settings + .env
│   │   ├── main.py               # FastAPI app, CORS, router registration
│   │   ├── routers/
│   │   │   ├── upload.py         # POST /api/upload — file parsing + AI analysis
│   │   │   └── charts.py        # POST /api/chart-data — aggregated data
│   │   └── services/
│   │       ├── file_processor.py       # CSV/XLSX → pandas DataFrame
│   │       ├── ai_analyzer.py          # Gemini integration & prompt engineering
│   │       └── chart_data_builder.py   # Data aggregation for charts
│   ├── tests/                    # pytest test suite (39 tests)
│   ├── Dockerfile                # Production container image
│   ├── requirements.txt
│   └── .env.example
│
├── web/                          # React SPA (Vite + TypeScript)
│   ├── src/
│   │   ├── api/client.ts         # API client (configurable base URL)
│   │   ├── i18n/                 # Internationalization (ES/EN)
│   │   ├── components/
│   │   │   ├── FileUpload.tsx          # Drag-and-drop file upload
│   │   │   ├── LoadingState.tsx        # AI processing indicator
│   │   │   ├── AnalysisCard.tsx        # AI suggestion cards
│   │   │   ├── ChartRenderer.tsx       # Recharts-based chart rendering
│   │   │   └── Dashboard.tsx           # Interactive dashboard grid
│   │   ├── tests/                # Vitest + React Testing Library (32 tests)
│   │   ├── App.tsx               # Main application with state management
│   │   └── index.css             # Dark-themed professional design
│   ├── Dockerfile                # Multi-stage build (Node + nginx)
│   └── nginx.conf                # Reverse proxy config for Docker
│
└── docker-compose.yml            # Single-command local deployment
```

---

## 🚀 Getting Started

### Prerequisites

| Tool        | Version  | Required for         |
| ----------- | -------- | -------------------- |
| Gemini Key  | —        | Both options         |
| Python      | 3.10+    | Manual setup         |
| Node.js     | 18+      | Manual setup         |
| npm         | 9+       | Manual setup         |
| Docker      | 20+      | Docker Compose setup |

Get a free Gemini API key at [Google AI Studio](https://aistudio.google.com/apikey).

### Quick Reference — URLs & Ports

| Service | Manual Setup            | Docker Compose          |
| ------- | ----------------------- | ----------------------- |
| Web App | http://localhost:5173   | http://localhost:3000   |
| API     | http://localhost:8000   | http://localhost:8000   |
| Swagger | http://localhost:8000/docs | http://localhost:8000/docs |

> **Note:** The ports differ because manual mode uses Vite's dev server (5173) with hot-reload, while Docker serves a production build via nginx (3000). Both can coexist without port conflicts.

---

### Option 1 — Manual Setup

Run each service independently in its own terminal. Best for **development** with hot-reload.

#### 1. API (Python + FastAPI)

```bash
cd api

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env and set your Gemini API key:
#   GEMINI_API_KEY=your_key_here

# Start the API server
uvicorn app.main:app --reload --port 8000
```

The API will be available at **http://localhost:8000**.  
Swagger docs: **http://localhost:8000/docs**

#### 2. Web (React + Vite)

```bash
cd web

# Install dependencies
npm install

# Start the development server
npm run dev
```

The app will be available at **http://localhost:5173**.

#### 3. Running Both Together (Manual)

Open two terminal windows:

**Terminal 1 — API:**
```bash
cd api && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Web:**
```bash
cd web && npm run dev
```

Navigate to **http://localhost:5173** and upload a spreadsheet.

---

### Option 2 — Docker Compose

Run everything with a single command. Best for **quick demos** and **production-like** environments.

#### 1. Configure the API key

```bash
cd api
cp .env.example .env
# Edit .env and set your Gemini API key:
#   GEMINI_API_KEY=your_key_here
```

#### 2. Build and start

```bash
# From the project root
docker compose up --build
```

The app will be available at **http://localhost:3000**.  
The API is also accessible directly at **http://localhost:8000**.

#### 3. Stop

```bash
docker compose down
```

#### 4. Rebuild after code changes

```bash
docker compose up --build
```

---

### Running Tests

```bash
# API tests (pytest)
cd api
source .venv/bin/activate    # or run inside the container
python -m pytest tests/ -v

# Web tests (Vitest)
cd web
npm test
```

---

## 📡 API Endpoints

| Method | Endpoint           | Description                                      |
| ------ | ------------------ | ------------------------------------------------ |
| GET    | `/api/health`      | Health check                                     |
| POST   | `/api/upload`      | Upload a file, parse it, and get AI suggestions  |
| POST   | `/api/chart-data`  | Get aggregated, chart-ready data for a chart     |

### `POST /api/upload`

- **Input**: `multipart/form-data` with a `file` field (`.csv` or `.xlsx`)
- **Output**:
```json
{
  "session_id": "uuid",
  "rows": 1500,
  "columns": ["Region", "Sales", "Date"],
  "suggestions": [
    {
      "title": "Distribución de Ventas por Región",
      "chart_type": "bar",
      "parameters": { "x_axis": "Region", "y_axis": "Sales", "aggregation": "sum" },
      "insight": "La región Norte lidera las ventas con un 35% del total."
    }
  ]
}
```

### `POST /api/chart-data`

- **Input**:
```json
{
  "session_id": "uuid",
  "chart_type": "bar",
  "parameters": { "x_axis": "Region", "y_axis": "Sales", "aggregation": "sum" }
}
```
- **Output**: `{ "data": [{ "name": "Norte", "value": 50000 }, ...] }`

---

## 🧪 Testing

### API — pytest (39 tests)

| Area                    | Coverage                                                     |
| ----------------------- | ------------------------------------------------------------ |
| Health endpoint         | Status check                                                 |
| Upload validation       | Extension, size, empty file, no extension rejection          |
| Upload success          | CSV parsing, session storage, AI mock integration            |
| Chart data endpoint     | Bar/line/area/pie/scatter, all aggregations, invalid columns |
| File processor service  | CSV encoding fallback, XLSX, unsupported format              |
| Chart data builder      | Aggregation math, top-N limits, Others grouping, scatter cap |
| AI analyzer service     | Missing API key, JSON parsing, markdown fence stripping      |

### Web — Vitest + React Testing Library (32 tests)

| Component       | Coverage                                                    |
| --------------- | ----------------------------------------------------------- |
| FileUpload      | Drop zone, file preview, drag-and-drop, size formatting     |
| LoadingState    | Processing text, spinner rendering                          |
| AnalysisCard    | Title, insight, chart type, add/remove toggle, all types    |
| Dashboard       | Empty state, card rendering, remove callbacks, chart mocks  |
| useTranslation  | Default locale, ES/EN, dynamic switching                    |
| API client      | Upload/chart-data requests, error handling, fallbacks       |

---

## 🧠 AI Prompt Engineering Approach

The core AI integration follows a structured approach designed for **consistency, precision, and actionable outputs**:

### Prompt Design Principles

1. **Role assignment**: The prompt instructs Gemini to act as an *expert data analyst*, providing domain-specific expertise in its suggestions.

2. **Rich context injection**: Rather than sending raw data, the system sends a **structured schema summary** to the LLM that includes:
   - Column names and data types
   - Non-null counts and unique value counts per column
   - Full numeric statistics (`describe()` output)
   - Sample data (first 5 rows)

3. **Strict output format**: The prompt explicitly defines the expected JSON structure with specific keys (`title`, `chart_type`, `parameters`, `insight`) and valid values for each, ensuring machine-parseable responses.

4. **Guard rails**: The prompt includes explicit rules such as:
   - Only use column names that exist in the dataset
   - Choose chart types that match the data types
   - Prioritize actionable insights
   - Return ONLY valid JSON (no markdown wrapping)

5. **Localization in prompt**: Titles and insights are requested in Spanish, keeping the UI language consistent without post-processing.

6. **Aggregation awareness**: The prompt understands aggregation types (`sum`, `mean`, `count`) so the backend can accurately group and aggregate data without guessing.

---

## 🔧 Technical Decisions

| Decision                        | Rationale                                                                  |
| ------------------------------- | -------------------------------------------------------------------------- |
| **FastAPI**                     | Async-first, auto-docs (Swagger), type-safe with Pydantic                 |
| **Pandas**                      | Industry standard for tabular data processing and statistical analysis     |
| **Gemini 2.5 Flash**            | Fast, cost-effective, excellent at structured JSON generation              |
| **google-genai**                | Official Google AI SDK with simple, modern API                             |
| **Vite + React + TypeScript**   | Fast dev server, type safety, modern toolchain                             |
| **Recharts**                    | React-native charting, declarative API, responsive, well-typed             |
| **Lucide React**                | Lightweight, tree-shakeable icon library                                   |
| **CSS custom properties**       | No CSS framework dependency, full control over dark theme                  |
| **Custom i18n**                 | Lightweight, type-safe translations without external dependency            |
| **In-memory session store**     | Simplifies MVP; easily replaceable with Redis for production               |
| **Server-side aggregation**     | Avoids sending raw datasets to the client; better performance and security |
| **Vitest**                      | Native Vite integration, fast, ESM-first test runner                       |
| **pytest**                      | Python standard for testing, async support, rich fixture system            |

---

## 📋 User Flow

1. **Upload** → Drag-and-drop or click to select a `.csv`/`.xlsx` file
2. **Process** → Click "Procesar Archivo"; the backend parses the data and sends the schema to Gemini
3. **Explore** → Review AI-generated analysis cards with chart types, titles, and insights
4. **Build** → Click "Agregar al Dashboard" on any card to add it to the live dashboard
5. **Interact** → Hover over charts for tooltips; remove cards as needed
6. **Repeat** → Click "Nuevo Análisis" to start fresh with a different file

---

## 🌐 Deployment

The project supports deployment to cloud platforms like [Render](https://render.com):

- **API** — Deploy as a **Web Service** with Root Directory set to `api` (uses the Dockerfile).
- **Web** — Deploy as a **Static Site** with Root Directory set to `web`, Build Command `npm ci && npm run build`, and Publish Directory `dist`.
- Set the environment variable `VITE_API_BASE` on the web service to point to the API's public URL (e.g., `https://your-api.onrender.com/api`).
- Set `GEMINI_API_KEY` as an environment variable on the API service.

---

## 🔮 Upcoming Features

- **Multi-language support (i18n)** — Full runtime language switching between Spanish, English, and additional locales
- **Security enhancements** — Rate limiting, input sanitization, and authentication for API endpoints
- **Support for additional AI models** — Integration with OpenAI GPT, Anthropic Claude, and other LLM providers
- **User-provided API keys** — Allow users to enter and use their own AI provider API keys directly from the UI

---

## License

MIT

---

© Kevin Mencos
