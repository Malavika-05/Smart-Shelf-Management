import React, { useState, useRef } from 'react';
import axios from 'axios';
import './LiveShelfMonitoring.css';

const LiveShelfMonitoring = () => {
  const [viewMode, setViewMode] = useState('detection');
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleImageSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      setError(null);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
      
      // Automatically process the image
      handleImageUpload(file);
    }
  };

  const handleImageUpload = async (file) => {
    if (!file) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post('/api/detect/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setDetections(response.data.items || []);
      console.log('YOLO Detections:', response.data.items);
    } catch (err) {
      setError('Failed to process image. Make sure the backend is running.');
      console.error('Upload error:', err);
      setDetections([]);
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
      handleImageUpload(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  return (
    <div className="card">
      <div className="card-header-with-toggle">
        <h2 className="card-title">Live Shelf View</h2>
        <div className="view-toggle">
          <button
            className={`toggle-button ${viewMode === 'original' ? 'active' : ''}`}
            onClick={() => setViewMode('original')}
          >
            Original View
          </button>
          <button
            className={`toggle-button ${viewMode === 'detection' ? 'active' : ''}`}
            onClick={() => setViewMode('detection')}
          >
            Detection Overlay
          </button>
        </div>
      </div>
      
      <div className="upload-section">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleImageSelect}
          accept="image/*"
          style={{ display: 'none' }}
        />
        <button
          className="upload-button"
          onClick={() => fileInputRef.current?.click()}
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Upload Image'}
        </button>
        {selectedImage && (
          <span className="file-name">{selectedImage.name}</span>
        )}
      </div>

      {error && (
        <div className="error-message" style={{ margin: '10px 0', padding: '10px', background: '#ffebee', color: '#c62828', borderRadius: '4px' }}>
          {error}
        </div>
      )}

      <div 
        className="video-container"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        {imagePreview ? (
          <div className="image-preview-container">
            <img 
              src={imagePreview} 
              alt="Shelf view" 
              className="shelf-image"
            />
            {viewMode === 'detection' && detections.length > 0 && (
              <div className="detection-overlay">
                <div className="detection-info">
                  <h4>Detected Products:</h4>
                  <ul>
                    {detections.map((item, idx) => (
                      <li key={idx}>
                        {item.productName} - Qty: {item.quantity} (Confidence: {item.confidence}%)
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="video-placeholder">
            <div className="placeholder-content">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <rect x="2" y="4" width="20" height="16" rx="2" />
                <path d="M10 8l6 4-6 4V8z" />
              </svg>
              <p>Drag & drop an image here or click "Upload Image"</p>
              <p style={{ fontSize: '12px', color: '#999', marginTop: '8px' }}>
                Upload a shelf image to detect products using YOLO
              </p>
              {viewMode === 'detection' && (
                <span className="overlay-badge">Detection Overlay Active</span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveShelfMonitoring;
