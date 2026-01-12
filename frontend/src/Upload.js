import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function Upload() {
  const [file, setFile] = useState(null);
  const [parsedData, setParsedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [category, setCategory] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }
    setLoading(true);
    setError('');
    setParsedData(null);
    const formData = new FormData();
    formData.append('receipt', file);

    try {
      const response = await axios.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setParsedData(response.data);
    } catch (err) {
      setError('Error uploading and parsing the receipt. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDataChange = (e, index, field) => {
    const { name, value } = e.target;
    if (parsedData) {
      if (field) { // For items
        const updatedItems = [...parsedData.items];
        updatedItems[index][field] = value;
        setParsedData({ ...parsedData, items: updatedItems });
      } else { // For top-level fields
        setParsedData({ ...parsedData, [name]: value });
      }
    }
  };

  const handleSave = async () => {
    if (!parsedData) {
      setError('No data to save.');
      return;
    }

    const dataToSave = { ...parsedData, category };

    try {
      const response = await axios.post('/save', dataToSave);
      console.log('Save successful:', response.data);
      alert('Receipt saved successfully!');
      // Optionally, clear the form or redirect
      setParsedData(null);
      setFile(null);
      setCategory('');
    } catch (err) {
      setError('Error saving the receipt. Please try again.');
      console.error(err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Receipt Tracker</h1>
        <div className="upload-section">
          <input type="file" onChange={handleFileChange} />
          <button onClick={handleUpload} disabled={loading}>
            {loading ? 'Processing...' : 'Upload and Parse'}
          </button>
        </div>
        {error && <p className="error">{error}</p>}
      </header>
      <main>
        {parsedData && (
          <div className="results-section">
            <h2>Parsed Receipt Data</h2>
            <div className="form-group">
                <label>Store Name:</label>
                <input type="text" name="store_name" value={parsedData.store_name || ''} onChange={handleDataChange} />
            </div>
            <div className="form-group">
                <label>Date:</label>
                <input type="text" name="date" value={parsedData.date || ''} onChange={handleDataChange} />
            </div>
            <div className="form-group">
                <label>Total:</label>
                <input type="number" name="total" value={parsedData.total || ''} onChange={handleDataChange} />
            </div>
            <h3>Items</h3>
            <div className="items-list">
              {parsedData.items && parsedData.items.map((item, index) => (
                <div key={index} className="item">
                  <input type="text" value={item.description || ''} onChange={(e) => handleDataChange(e, index, 'description')} placeholder="Description" />
                  <input type="number" value={item.price || ''} onChange={(e) => handleDataChange(e, index, 'price')} placeholder="Price" />
                </div>
              ))}
            </div>
             <div className="form-group">
                <label>Category:</label>
                <input type="text" name="category" placeholder="e.g., Groceries, Gas" value={category} onChange={(e) => setCategory(e.target.value)} />
            </div>
            <button onClick={handleSave} className="save-btn">Save</button>
          </div>
        )}
      </main>
    </div>
  );
}

export default Upload;
