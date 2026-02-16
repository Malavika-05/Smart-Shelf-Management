from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import torch

# Patch torch.load to allow loading YOLO models (PyTorch 2.6+ requires weights_only=False)
# This is safe since we're loading our own trained model
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
import io
from datetime import datetime, timedelta
from typing import List, Optional
import json
from pathlib import Path
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load YOLO model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "best.pt")
model = None
latest_detections = []
detection_history = []

def load_model():
    """Load the YOLO model"""
    global model
    logger.info(f"Checking for model at: {MODEL_PATH}")
    logger.info(f"Absolute path: {os.path.abspath(MODEL_PATH)}")
    logger.info(f"File exists: {os.path.exists(MODEL_PATH)}")
    logger.info(f"PyTorch version: {torch.__version__}")
    
    if os.path.exists(MODEL_PATH):
        try:
            logger.info(f"Loading YOLO model from {MODEL_PATH}")
            model = YOLO(MODEL_PATH)
            logger.info(f"Model loaded successfully from {MODEL_PATH}")
            if hasattr(model, 'names'):
                logger.info(f"Model classes: {model.names}")
            else:
                logger.warning("Model does not have 'names' attribute")
            logger.info(f"Model type: {type(model)}")
            return True
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            logger.error(traceback.format_exc())
            return False
    else:
        logger.error(f"Model file not found at {MODEL_PATH}")
        logger.error(f"Current working directory: {os.getcwd()}")
        logger.error(f"Directory contents: {os.listdir(os.path.dirname(MODEL_PATH)) if os.path.exists(os.path.dirname(MODEL_PATH)) else 'Directory does not exist'}")
        return False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    success = load_model()
    if not success:
        logger.error("Failed to load model on startup!")
    else:
        logger.info("Application startup complete")
    yield
    # Shutdown (if needed)
    logger.info("Shutting down application...")

app = FastAPI(title="Smart Shelf Management API", lifespan=lifespan)

# CORS middleware to allow React frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_image(image_bytes: bytes) -> dict:
    """Process image with YOLO model and return detections"""
    global latest_detections, detection_history, model
    
    # Try to load model if not loaded
    if model is None:
        logger.warning("Model not loaded, attempting to load now...")
        success = load_model()
        if not success or model is None:
            logger.error("Model not loaded and failed to load on demand")
            raise HTTPException(status_code=500, detail="Model not loaded. Please check server logs.")
    
    try:
        logger.info(f"Processing image, size: {len(image_bytes)} bytes")
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            raise HTTPException(status_code=400, detail="Invalid image format")
        
        logger.info(f"Image decoded successfully, shape: {img.shape}")
        
        # Run YOLO inference
        logger.info("Running YOLO inference...")
        results = model(img, conf=0.25)  # Confidence threshold
        logger.info(f"YOLO inference completed, found {len(results)} result(s)")
        
        # Process results
        items = []
        detected_classes = {}
        
        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                logger.info("No detections found in image")
                continue
                
            boxes = result.boxes
            logger.info(f"Processing {len(boxes)} detections")
            
            for box in boxes:
                try:
                    # Get class name and confidence
                    cls_id = int(box.cls[0].item() if hasattr(box.cls[0], 'item') else box.cls[0])
                    confidence = float(box.conf[0].item() if hasattr(box.conf[0], 'item') else box.conf[0]) * 100
                    
                    # Get class name from model
                    if hasattr(model, 'names') and cls_id in model.names:
                        class_name = model.names[cls_id]
                    else:
                        class_name = f"Class_{cls_id}"
                    
                    logger.debug(f"Detected: {class_name} with confidence {confidence:.2f}%")
                    
                    # Count items by class
                    if class_name not in detected_classes:
                        detected_classes[class_name] = {
                            'count': 0,
                            'confidences': []
                        }
                    detected_classes[class_name]['count'] += 1
                    detected_classes[class_name]['confidences'].append(confidence)
                except Exception as e:
                    logger.error(f"Error processing box: {e}")
                    logger.error(traceback.format_exc())
                    continue
        
        # Convert to frontend format
        for class_name, data in detected_classes.items():
            avg_confidence = sum(data['confidences']) / len(data['confidences'])
            # Generate SKU from class name (simple mapping)
            sku = generate_sku(class_name)
            
            items.append({
                'productName': class_name.replace('_', ' ').title(),
                'sku': sku,
                'quantity': data['count'],
                'confidence': round(avg_confidence, 1)
            })
        
        logger.info(f"Processed {len(items)} product types")
        
        # Update latest detections
        latest_detections = items
        detection_history.append({
            'timestamp': datetime.now().isoformat(),
            'items': items
        })
        
        # Keep only last 100 detections in history
        if len(detection_history) > 100:
            detection_history.pop(0)
        
        return {'items': items}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

def generate_sku(product_name: str) -> str:
    """Generate a SKU code from product name"""
    # Simple SKU generation - you can customize this
    words = product_name.replace('_', ' ').split()
    if len(words) >= 2:
        sku = f"{words[0][:2].upper()}-{words[1][:3].upper()}-{hash(product_name) % 10000:04d}"
    else:
        sku = f"{words[0][:5].upper()}-{hash(product_name) % 10000:04d}"
    return sku

@app.post("/api/detect/upload")
async def upload_image(file: UploadFile = File(...)):
    """Upload an image and get detections"""
    try:
        logger.info(f"Received upload request: {file.filename}, content_type: {file.content_type}")
        
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image_bytes = await file.read()
        logger.info(f"Read {len(image_bytes)} bytes from uploaded file")
        
        result = process_image(image_bytes)
        logger.info(f"Successfully processed image, returning {len(result.get('items', []))} items")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_image: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")

@app.get("/api/detect")
async def get_detections():
    """Get latest detections"""
    if not latest_detections:
        # Return empty or sample data if no detections yet
        return {
            "items": []
        }
    return {
        "items": latest_detections
    }

@app.get("/api/forecast")
async def get_forecast():
    """Get forecast and prediction data"""
    if not detection_history:
        return {
            "forecasts": [],
            "historical": []
        }
    
    # Generate forecasts based on detection history
    forecasts = []
    historical = []
    
    # Analyze trends from history
    product_trends = {}
    for detection in detection_history[-20:]:  # Last 20 detections
        for item in detection['items']:
            sku = item['sku']
            if sku not in product_trends:
                product_trends[sku] = {
                    'productName': item['productName'],
                    'quantities': []
                }
            product_trends[sku]['quantities'].append(item['quantity'])
    
    # Generate forecasts
    for sku, data in product_trends.items():
        if len(data['quantities']) >= 2:
            # Simple trend calculation
            quantities = data['quantities']
            trend = quantities[-1] - quantities[0]
            current_qty = quantities[-1]
            
            if trend < 0 and current_qty > 0:
                # Decreasing trend - calculate time until empty
                rate_per_hour = abs(trend) / len(quantities) * 12  # Assuming 12 detections per hour
                if rate_per_hour > 0:
                    hours_until_empty = current_qty / rate_per_hour
                    suggested_restock = max(0, hours_until_empty - 1)
                    
                    forecasts.append({
                        'sku': sku,
                        'productName': data['productName'],
                        'timeUntilEmpty': f"{hours_until_empty:.1f} hours",
                        'suggestedRestock': f"{suggested_restock:.1f} hours"
                    })
    
    # Generate historical data
    for i, detection in enumerate(detection_history[-24:]):  # Last 24 detections
        total_stock = sum(item['quantity'] for item in detection['items'])
        historical.append({
            'time': datetime.fromisoformat(detection['timestamp']).strftime("%H:%M"),
            'stock': total_stock,
            'predicted': int(total_stock * 0.95)  # Simple prediction
        })
    
    return {
        "forecasts": forecasts,
        "historical": historical
    }

@app.get("/api/alerts")
async def get_alerts():
    """Get alerts and notifications"""
    alerts = []
    
    if latest_detections:
        for item in latest_detections:
            # Generate alerts for low stock
            if item['quantity'] < 5:
                alerts.append({
                    'id': f"alert-{item['sku']}",
                    'type': 'low_stock',
                    'severity': 'high' if item['quantity'] < 2 else 'medium',
                    'message': f"Low stock alert: {item['productName']} ({item['quantity']} remaining)",
                    'sku': item['sku'],
                    'productName': item['productName'],
                    'quantity': item['quantity'],
                    'timestamp': datetime.now().isoformat()
                })
            
            # Generate alerts for restock needed
            if item['quantity'] < 3:
                alerts.append({
                    'id': f"restock-{item['sku']}",
                    'type': 'restock_needed',
                    'severity': 'high',
                    'message': f"Restock required: {item['productName']}",
                    'sku': item['sku'],
                    'productName': item['productName'],
                    'quantity': item['quantity'],
                    'timestamp': datetime.now().isoformat()
                })
    
    return {
        "alerts": alerts
    }

@app.get("/api/analytics")
async def get_analytics(range: str = "24h"):
    """Get analytics data"""
    # Calculate range
    if range == "24h":
        hours = 24
    elif range == "7d":
        hours = 168
    elif range == "30d":
        hours = 720
    else:
        hours = 24
    
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    # Filter detection history by range
    filtered_history = [
        d for d in detection_history
        if datetime.fromisoformat(d['timestamp']) >= cutoff_time
    ]
    
    # Calculate sales trend
    sales_trend = []
    product_distribution = {}
    total_detections = 0
    confidence_scores = []
    
    for detection in filtered_history:
        timestamp = datetime.fromisoformat(detection['timestamp'])
        total_items = sum(item['quantity'] for item in detection['items'])
        sales_trend.append({
            'time': timestamp.strftime("%Y-%m-%d %H:%M"),
            'value': total_items
        })
        
        for item in detection['items']:
            product_name = item['productName']
            if product_name not in product_distribution:
                product_distribution[product_name] = 0
            product_distribution[product_name] += item['quantity']
            confidence_scores.append(item['confidence'])
            total_detections += 1
    
    # Top products
    top_products = sorted(
        [{'name': k, 'value': v} for k, v in product_distribution.items()],
        key=lambda x: x['value'],
        reverse=True
    )[:10]
    
    # Calculate metrics
    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
    
    return {
        "salesTrend": sales_trend,
        "productDistribution": [{'name': k, 'value': v} for k, v in product_distribution.items()],
        "topProducts": top_products,
        "detectionAccuracy": round(avg_confidence, 1),
        "totalDetections": total_detections,
        "averageConfidence": round(avg_confidence, 1)
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "model_path": MODEL_PATH if model is None else "loaded"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
