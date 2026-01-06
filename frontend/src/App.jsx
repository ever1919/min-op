import React, { useState, useEffect } from 'react';
import { Upload, FileText, Download, Loader2, CheckCircle, X } from 'lucide-react';

export default function CVOnePagerGenerator() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [generatedPager, setGeneratedPager] = useState(null);
  const [coeSelected, setCoeSelected] = useState('');
  const [towerSelected, setTowerSelected] = useState('');
  const [coeOptions, setCoeOptions] = useState({});
  const [error, setError] = useState('');
  const [coeLoadError, setCoeLoadError] = useState('');

  useEffect(() => {
    const loadCoeOptions = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/coe-towers');
        const data = await response.json();
        setCoeOptions(data);
      } catch (err) {
        setCoeLoadError('Failed to load COE data. Please refresh the page.');
        console.error('Failed to load COE options:', err);
      }
    };

    loadCoeOptions();
  }, []);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFile(files[0]);
    }
  };

  const handleFile = (file) => {
    setError('');

    // Validate file
    if (file.type !== 'application/pdf') {
      setError('Please upload a PDF file');
      return;
    }

    if (file.size > 200 * 1024 * 1024) {
      setError('File size must be less than 200MB');
      return;
    }

    setUploadedFile(file);
  };

  const handleGenerate = () => {
    setError('');
    if (!coeSelected) { setError('Please select a COE'); return; }
    if (!uploadedFile) { setError('Please upload a PDF file'); return; }
    processCV(uploadedFile);
  };

  const processCV = async (file) => {
    setIsProcessing(true);
    setError('');

    try {
      // Convert file to base64 for API transmission
      const base64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });

      console.log('Sending to backend:', {
        coe_selected: coeSelected,
        tower_selected: towerSelected
      });

      const response = await fetch('http://localhost:8000/generate-onepager', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          file: base64,
          filename: file.name,
          coe_selected: coeSelected,
          tower_selected: towerSelected
        })
      });

      if (!response.ok) {
        throw new Error('Failed to process CV');
      }

      // Response is the PPTX file blob directly
      const blob = await response.blob();

      // Store blob for download
      setGeneratedPager({
        blob: blob,
        filename: file.name.replace('.pdf', '.pptx')
      });

    } catch (err) {
      setError(err.message || 'An error occurred while processing your CV');
      console.error('Processing error:', err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = async () => {
    try {
      // File is already downloaded as blob, just trigger browser download
      const url = window.URL.createObjectURL(generatedPager.blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = generatedPager.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

    } catch (err) {
      setError(err.message || 'Failed to download file');
      console.error('Download error:', err);
    }
  };

  const handleReset = () => {
    setUploadedFile(null);
    setGeneratedPager(null);
    setError('');
    setCoeSelected('');
    setTowerSelected('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50">
      {/* Header with Accenture branding */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center space-x-2">
            {/* Greater than symbol */}
            <svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" width="40" height="40">
              <path d="M0 28.75L22.07 20.54L0 11.92V0.5L37.8 15.72V25.19L0 40.5V28.75Z" fill="#A100F2" />
            </svg>

            {/* Accenture text */}
            <svg viewBox="0 0 153 40" fill="none" xmlns="http://www.w3.org/2000/svg" width="140" height="40">
              <path d="M5.76753 39.9342C2.60469 39.9342 0 38.3554 0 34.8263V34.6406C0 30.3686 3.72099 28.8827 8.2792 28.8827H10.4188V28.0468C10.4188 26.2823 9.67457 25.2607 7.81407 25.2607C6.13963 25.2607 5.30241 26.1894 5.20938 27.4896H0.558148C0.930247 23.589 4.00006 21.7316 8.09315 21.7316C12.2793 21.7316 15.3491 23.4962 15.3491 27.8611V39.5627H10.6048V37.5196C9.67457 38.8198 8.09315 39.9342 5.76753 39.9342ZM10.4188 33.8048V32.1331H8.46525C6.04661 32.1331 4.83728 32.7832 4.83728 34.362V34.5477C4.83728 35.7551 5.58148 36.5909 7.25593 36.5909C8.93037 36.498 10.4188 35.5693 10.4188 33.8048ZM26.419 39.9342C21.5817 39.9342 18.0468 36.9624 18.0468 31.0187V30.7401C18.0468 24.7964 21.7678 21.6388 26.419 21.6388C30.4191 21.6388 33.6749 23.6819 34.047 28.2326H29.3958C29.1167 26.5609 28.1865 25.4465 26.512 25.4465C24.4655 25.4465 22.9771 27.1181 22.9771 30.5543V31.1115C22.9771 34.6406 24.2794 36.2194 26.512 36.2194C28.1865 36.2194 29.3958 35.0121 29.6749 33.0618H34.1401C33.861 37.1481 31.1633 39.9342 26.419 39.9342ZM44.6519 39.9342C39.8146 39.9342 36.2796 36.9624 36.2796 31.0187V30.7401C36.2796 24.7964 40.0006 21.6388 44.6519 21.6388C48.6519 21.6388 51.9078 23.6819 52.2799 28.2326H47.6286C47.3496 26.5609 46.4193 25.4465 44.7449 25.4465C42.6983 25.4465 41.2099 27.1181 41.2099 30.5543V31.1115C41.2099 34.6406 42.5123 36.2194 44.7449 36.2194C46.4193 36.2194 47.6286 35.0121 47.9077 33.0618H52.3729C52.0938 37.1481 49.3961 39.9342 44.6519 39.9342ZM62.9777 39.9342C57.9544 39.9342 54.5125 36.9624 54.5125 31.1115V30.7401C54.5125 24.8892 58.1404 21.6388 62.8847 21.6388C67.2569 21.6388 70.8848 24.0534 70.8848 29.9042V32.0402H59.4428C59.6288 35.1978 61.0242 36.4051 63.0707 36.4051C64.9312 36.4051 65.9545 35.3836 66.3266 34.1763H70.8848C70.3267 37.4267 67.5359 39.9342 62.9777 39.9342ZM59.5358 28.7898H66.0475C65.9545 26.1894 64.7452 25.075 62.7917 25.075C61.3033 25.1678 59.9079 26.0037 59.5358 28.7898ZM73.8616 22.1031H78.7919V24.7035C79.6291 23.0318 81.3966 21.7316 84.0943 21.7316C87.2572 21.7316 89.3967 23.6819 89.3967 27.8611V39.5627H84.4664V28.604C84.4664 26.5609 83.6292 25.6322 81.8617 25.6322C80.1873 25.6322 78.7919 26.6538 78.7919 28.8827V39.5627H73.8616V22.1031ZM98.4201 16.8095V22.1031H101.769V25.7251H98.4201V33.9905C98.4201 35.2907 98.9783 35.9408 100.188 35.9408C100.932 35.9408 101.397 35.8479 101.862 35.6622V39.4699C101.304 39.6556 100.281 39.8413 99.0713 39.8413C95.2573 39.8413 93.4898 38.0768 93.4898 34.5477V25.7251H91.4433V22.1031H93.4898V18.8527L98.4201 16.8095ZM120.188 39.5627H115.351V36.9624C114.513 38.634 112.839 39.9342 110.234 39.9342C107.071 39.9342 104.746 37.9839 104.746 33.8976V22.1031H109.676V33.2476C109.676 35.2907 110.513 36.2194 112.188 36.2194C113.862 36.2194 115.258 35.105 115.258 32.9689V22.1031H120.188V39.5627ZM123.816 22.1031H128.746V25.3536C129.769 23.0318 131.444 21.9174 134.049 21.9174V26.7466C130.7 26.7466 128.746 27.7682 128.746 30.6472V39.6556H123.816V22.1031ZM144.002 39.9342C138.979 39.9342 135.537 36.9624 135.537 31.1115V30.7401C135.537 24.8892 139.165 21.6388 143.909 21.6388C148.281 21.6388 151.909 24.0534 151.909 29.9042V32.0402H140.56C140.746 35.1978 142.142 36.4051 144.188 36.4051C146.049 36.4051 147.072 35.3836 147.444 34.1763H152.002C151.258 37.4267 148.56 39.9342 144.002 39.9342ZM140.467 28.7898H147.072C146.979 26.1894 145.77 25.075 143.816 25.075C142.328 25.1678 140.932 26.0037 140.467 28.7898Z" fill="#A100F2" />
            </svg>
          </div>
        </div>
      </header>


      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Title Section */}
        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-4">
            <FileText className="w-12 h-12 text-purple-600" />
            <h1 className="text-5xl font-bold text-gray-900">CV One Pager Generator</h1>
          </div>
          <p className="text-xl text-gray-600 ml-16">Upload a CV in PDF format</p>
        </div>

        {/* Form Container */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8 space-y-6 mb-8">
          {coeLoadError && (
            <div className="flex items-center gap-3 text-red-700 bg-red-50 border border-red-200 p-4 rounded-lg">
              <X className="w-5 h-5" />
              <span>{coeLoadError}</span>
            </div>
          )}

          {/* COE Dropdown */}
          <div>
            <label className="block text-lg font-semibold text-gray-700 mb-2">Center of Excellence</label>
            <select
              value={coeSelected}
              onChange={(e) => { setCoeSelected(e.target.value); setTowerSelected(''); }}
              className="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-600"
            >
              <option value="">Select COE</option>
              {Object.keys(coeOptions).map((coe) => <option key={coe} value={coe}>{coe}</option>)}
            </select>
          </div>

          {/* Tower Dropdown */}
          <div>
            <label className="block text-lg font-semibold text-gray-700 mb-2">Tower</label>
            <select
              value={towerSelected}
              onChange={(e) => setTowerSelected(e.target.value)}
              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-600"
            >
              <option value="">Select Tower</option>
              {coeSelected && coeOptions[coeSelected] && coeOptions[coeSelected].map(t => <option key={t} value={t}>{t}</option>)}
            </select>
          </div>

          {/* Upload CV */}
          <div>
            <label className="block text-lg font-semibold text-gray-700 mb-2">Upload CV (PDF)</label>
            <div
              onDragEnter={handleDragEnter}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-lg p-6 text-center transition-all ${isDragging ? 'border-purple-600 bg-purple-50' : 'border-gray-300 bg-gray-50'}`}
            >
              <Upload className="w-8 h-8 mx-auto text-gray-400 mb-2" />
              <p className="text-gray-600 mb-3">Drag & drop your PDF here or</p>
              <input id="form-file-input" type="file" accept=".pdf" onChange={(e) => { if (e.target.files[0]) handleFile(e.target.files[0]); }} className="hidden" />
              <label htmlFor="form-file-input" className="inline-block bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg cursor-pointer">Browse files</label>
              {uploadedFile && <p className="mt-3 text-sm text-gray-700">Selected: <strong>{uploadedFile.name}</strong></p>}
            </div>
          </div>

          {/* Error message */}
          {error && <div className="text-red-600 text-sm bg-red-50 border border-red-200 p-3 rounded-lg">{error}</div>}

          {/* Generate Button */}
          <div className="flex gap-4 pt-4">
            <button
              onClick={handleGenerate}
              disabled={isProcessing || !coeSelected || !uploadedFile}
              className="flex-1 bg-purple-700 text-white py-3 rounded-lg font-semibold hover:bg-purple-800 transition disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              {isProcessing ? 'Generating...' : 'Generate One-Pager'}
            </button>
          </div>
        </div>

        {/* Processing State */}
        {isProcessing && (
          <div className="bg-white rounded-2xl shadow-xl p-16">
            <div className="flex flex-col items-center space-y-6">
              <Loader2 className="w-20 h-20 text-purple-600 animate-spin" />
              <div className="text-center">
                <h3 className="text-2xl font-semibold text-gray-900 mb-2">Processing your CV...</h3>
                <p className="text-gray-600 text-lg">Generating your one-pager document</p>
              </div>
            </div>
          </div>
        )}

        {/* Success State */}
        {uploadedFile && !isProcessing && generatedPager && (
          <div className="bg-white rounded-2xl shadow-xl p-12">
            <div className="flex flex-col items-center space-y-8">
              <div className="p-6 bg-green-50 rounded-full">
                <CheckCircle className="w-20 h-20 text-green-600" />
              </div>

              <div className="text-center">
                <h3 className="text-3xl font-semibold text-gray-900 mb-3">One-Pager Generated Successfully!</h3>
                <p className="text-gray-600 text-lg mb-2">File: <span className="font-medium">{uploadedFile.name}</span></p>
                <p className="text-gray-500">Size: {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={handleDownload}
                  className="flex items-center space-x-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-4 px-10 rounded-lg transition-colors text-lg"
                >
                  <Download className="w-6 h-6" />
                  <span>Download One-Pager</span>
                </button>

                <button
                  onClick={handleReset}
                  className="flex items-center space-x-3 bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-4 px-10 rounded-lg transition-colors text-lg"
                >
                  <Upload className="w-6 h-6" />
                  <span>Upload Another CV</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="max-w-6xl mx-auto px-6 py-8 text-center text-gray-500">
        <p className="text-sm">Powered by Accenture • Confidential and secure processing</p>
      </footer>
    </div>
  );
}