# Stock Trading Dashboard

A comprehensive trading dashboard for tracking trades, journaling, and getting AI-powered insights.

## Features

### Dashboard

- Win/Loss ratio with Donut Chart visualization
- Profit/Loss tracking in real-time
- Swing/Day trade toggle for filtered views
- Responsive design for all devices

### Trade Management

- Manual trade entry with detailed fields
- Trade table with filtering capabilities
- Auto-detection of Win/Loss based on proceeds vs cost basis

### Journal System

- Trade-specific journal entries
- Daily general journal notes
- AI-powered insights and summaries from journal data

## Architecture

- **Backend**: Python Flask with RESTful API
- **Frontend**: Next.js with TypeScript
- **Database**: PostgreSQL for data persistence
- **AI**: OpenAI integration for insights
- **Styling**: Tailwind CSS for responsive design

## Tech Stack

### Backend

- Python 3.9+
- Flask 2.3+
- SQLAlchemy
- psycopg2-binary
- python-dotenv
- openai

### Frontend

- Next.js 14
- TypeScript
- Tailwind CSS
- Chart.js (for donut charts)
- React Hook Form

### Database

- PostgreSQL 14+

## Setup Instructions

### Prerequisites

- Python 3.9+
- Node.js 18+
- PostgreSQL
- OpenAI API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

### Environment Variables

Create `.env` files in both backend and frontend directories:

**Backend (.env)**

```
DATABASE_URL=postgresql://username:password@localhost:5432/trading_dashboard
OPENAI_API_KEY=your_openai_api_key
FLASK_SECRET_KEY=your_secret_key
```

**Frontend (.env.local)**

```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

### Database Setup

```bash
# Create database
createdb trading_dashboard

# Run migrations
cd backend
python manage.py db upgrade
```

### Running the Application

```bash
# Backend (Terminal 1)
cd backend
python app.py

# Frontend (Terminal 2)
cd frontend
npm run dev
```

Access the application at `http://localhost:3000`

## API Endpoints

### Trades

- `GET /api/trades` - Get all trades
- `POST /api/trades` - Create new trade
- `PUT /api/trades/<id>` - Update trade
- `DELETE /api/trades/<id>` - Delete trade

### Journal

- `GET /api/journal` - Get all journal entries
- `POST /api/journal` - Create journal entry
- `GET /api/journal/insights` - Get AI insights

### Dashboard

- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/chart` - Get chart data

## Project Structure

```
trading-insights/
├── backend/
│   ├── app.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── types/
│   ├── public/
│   └── package.json
└── README.md
```
