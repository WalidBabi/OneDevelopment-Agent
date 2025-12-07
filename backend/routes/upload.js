const express = require('express');
const multer = require('multer');
const axios = require('axios');
const router = express.Router();

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Upload endpoint for HeyGen assets
router.post('/heygen', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const filePurpose = req.body.file_purpose || 'avatar';
    
    // Create FormData for HeyGen API
    const FormData = require('form-data');
    const form = new FormData();
    form.append('file', req.file.buffer, {
      filename: req.file.originalname,
      contentType: req.file.mimetype,
    });
    form.append('file_purpose', filePurpose);

    // Upload to HeyGen
    const response = await axios.post(
      'https://api.heygen.com/v1/asset/upload',
      form,
      {
        headers: {
          ...form.getHeaders(),
          'X-Api-Key': process.env.REACT_APP_HEYGEN_API_KEY || 'sk_V2_hgu_kJF0dzYXUXD_KkIYxjBhIQKfPa2yE7ScO4vCNIrAuQCT',
        },
      }
    );

    console.log('HeyGen upload response:', response.data);
    res.json(response.data);
  } catch (error) {
    console.error('Upload error:', error.response?.data || error.message);
    res.status(500).json({ 
      error: 'Upload failed',
      details: error.response?.data || error.message 
    });
  }
});

module.exports = router;
