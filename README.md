# Smart Shelf Management Dashboard

A modern, clean, and academic-looking web dashboard UI for a Smart Shelf Management System used in grocery stores.

## Features

- **Home Dashboard**: Live shelf monitoring, detected items, stock levels, forecasts, and alerts
- **Analytics Page**: Detailed analytics with charts, metrics, and product distribution
- **Alerts Page**: Comprehensive alerts management with filtering and detailed views
- **Live Shelf Monitoring**: Real-time camera feed with detection overlay toggle
- **Detected Items Summary**: Table view of all detected products with SKU, quantity, and confidence scores
- **Stock Level Visualization**: Visual progress bars showing stock levels with color-coded indicators
- **Forecast & Prediction**: Restock forecasts with historical stock trends and predicted timelines
- **Alerts Panel**: Real-time alerts and notifications for low stock and restock requirements

## Technology Stack

### Frontend
- **React.js** - Frontend framework
- **React Router** - Client-side routing
- **Axios** - HTTP client for API calls
- **Recharts** - Chart library for data visualization
- **CSS3** - Styling with minimalistic, flat design

### Backend
- **FastAPI** - Python web framework for API
- **YOLO (Ultralytics)** - Object detection model
- **OpenCV** - Image processing
- **NumPy** - Numerical computations

## Design Philosophy

- Minimalistic and professional appearance
- Flat design (no gradients, no flashy colors)
- Neutral color palette (white, light gray, soft blue/green accents)
- Clean typography (Inter / Roboto)
- Responsive layout (desktop-first, scalable)
- Suitable for academic presentation and industry demo

## Installation

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will open at [http://localhost:3000](http://localhost:3000)

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure the YOLO model file (`best.pt`) is in `backend/models/` directory

5. Start the backend server:
```bash
python app.py
```

Or use the startup script:
```bash
./start.sh
```

The backend API will be available at [http://localhost:8000](http://localhost:8000)
API documentation (Swagger UI) available at [http://localhost:8000/docs](http://localhost:8000/docs)

**Note**: Make sure to start the backend server before the frontend for full functionality.

## Pages

- **/** - Home dashboard with all main components
- **/analytics** - Detailed analytics page with charts and metrics
- **/alerts** - Full alerts page with filtering and detailed views

## API Integration

The backend provides the following API endpoints:

- `GET /api/health` - Health check endpoint
- `GET /api/detect` - Returns latest detected items with product information
- `POST /api/detect/upload` - Upload an image and get detections (multipart/form-data)
- `GET /api/forecast` - Returns forecast data and predictions
- `GET /api/alerts` - Returns alerts and notifications
- `GET /api/analytics?range={24h|7d|30d}` - Returns analytics data

The frontend automatically proxies API requests to `http://localhost:8000` via `setupProxy.js`.

### API Response Format

**Detect Endpoint:**
```json
{
  "items": [
    {
      "productName": "Product Name",
      "sku": "SKU-CODE",
      "quantity": 10,
      "confidence": 95.5
    }
  ]
}
```

**Forecast Endpoint:**
```json
{
  "forecasts": [
    {
      "sku": "SKU-CODE",
      "productName": "Product Name",
      "timeUntilEmpty": "2.5 hours",
      "suggestedRestock": "1.5 hours"
    }
  ],
  "historical": [
    {
      "time": "10:00",
      "stock": 20,
      "predicted": 18
    }
  ]
}
```

**Analytics Endpoint:**
```json
{
  "salesTrend": [...],
  "productDistribution": [...],
  "topProducts": [...],
  "detectionAccuracy": 94.2,
  "totalDetections": 1247,
  "averageConfidence": 91.5
}
```

## Project Structure

```
Smart-Shelf-Management/
  ├── backend/
  │   ├── app.py                 # FastAPI application
  │   ├── requirements.txt       # Python dependencies
  │   ├── models/
  │   │   └── best.pt           # YOLO trained model
  │   ├── uploads/               # Uploaded images storage
  │   └── README.md             # Backend documentation
  ├── src/
  │   ├── components/
  │   │   ├── TopNavigation.js
  │   │   ├── LiveShelfMonitoring.js
  │   │   ├── DetectedItemsSummary.js
  │   │   ├── StockLevelVisualization.js
  │   │   ├── ForecastPrediction.js
  │   │   └── AlertsPanel.js
  │   ├── pages/
  │   │   ├── Home.js
  │   │   ├── Analytics.js
  │   │   └── Alerts.js
  │   ├── setupProxy.js         # API proxy configuration
  │   ├── App.js
  │   ├── App.css
  │   ├── index.js
  │   └── index.css
  └── README.md
```

## Error Handling

The application includes graceful error handling:
- Displays error messages when backend is unavailable
- Falls back to mock data for demonstration purposes
- Loading states during data fetching

## Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## License

This project is created for academic and demonstration purposes.

