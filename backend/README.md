# Smart Shelf Management Backend API

Backend API server for the Smart Shelf Management System using YOLO object detection.

## Features

- **YOLO Model Integration**: Loads and runs inference with the trained YOLO model (`best.pt`)
- **Image Upload & Detection**: Upload images and get real-time product detections
- **RESTful API**: Provides all endpoints required by the frontend
- **CORS Support**: Configured to work with React frontend on localhost:3000
- **Forecast & Analytics**: Generates forecasts and analytics based on detection history

## Installation

1. Create a virtual environment (recommended):
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
- `GET /api/health` - Check if the server and model are loaded

### Detection
- `GET /api/detect` - Get latest detections
- `POST /api/detect/upload` - Upload an image file and get detections
  - Body: `multipart/form-data` with `file` field containing image

### Forecast
- `GET /api/forecast` - Get forecast and prediction data
  - Returns: forecasts and historical stock trends

### Alerts
- `GET /api/alerts` - Get alerts and notifications
  - Returns: low stock and restock alerts

### Analytics
- `GET /api/analytics?range={24h|7d|30d}` - Get analytics data
  - Query params: `range` (optional, default: 24h)
  - Returns: sales trends, product distribution, top products, metrics

## Model File

The YOLO model should be located at `backend/models/best.pt`. If the model file is not found, the server will start but detection endpoints will return errors.

## Testing the API

### Upload an image for detection:
```bash
curl -X POST "http://localhost:8000/api/detect/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/your/image.jpg"
```

### Get latest detections:
```bash
curl http://localhost:8000/api/detect
```

### Get forecasts:
```bash
curl http://localhost:8000/api/forecast
```

### Get analytics:
```bash
curl "http://localhost:8000/api/analytics?range=24h"
```

## Frontend Integration

The frontend React app expects the backend to run on `http://localhost:8000`. Make sure to:

1. Start the backend server first
2. Configure the React app to proxy API requests (or update axios base URL)

## Notes

- The model is loaded once on server startup
- Detection history is kept in memory (last 100 detections)
- SKU generation is simplified - you may want to customize `generate_sku()` function
- Forecast calculations are based on simple trend analysis
- For production, consider adding:
  - Database for persistent storage
  - Authentication/Authorization
  - Rate limiting
  - Better error handling
  - Logging
