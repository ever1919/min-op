import React, { useState } from 'react';
import { Upload, FileText, Download, Loader2, CheckCircle, X } from 'lucide-react';

export default function CVOnePagerGenerator() {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [generatedPager, setGeneratedPager] = useState(null);
  const [error, setError] = useState('');

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

  const handleFileInput = (e) => {
    const files = e.target.files;
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
    processCV(file);
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

      // API ENDPOINT: POST request to process CV and generate PPTX
      // Replace '/api/generate-onepager' with your actual backend endpoint
      // This single endpoint handles everything:
      // PDF → TXT → LLM → Tabular format → PPTX (using python-pptx)
      // Expected request body: { file: base64String, filename: string }
      // Expected response: Binary PPTX file blob directly
      
      const response = await fetch('http://localhost:8000/generate-onepager', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add authentication header if needed
          // 'Authorization': `Bearer ${yourAuthToken}`
        },
        body: JSON.stringify({
          file: base64,
          filename: file.name
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
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-purple-50">
      {/* Header with Accenture branding */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center space-x-4">
            {/* Accenture Logo (using styled text as placeholder) */}
            <div className="flex items-center">
              <div className="text-3xl font-bold text-purple-600" style={{ fontFamily: 'Arial, sans-serif' }}>
                <span className="text-purple-600">&gt;</span>
                <span className="ml-1">Accenture</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        <div className="mb-12">
          <div className="flex items-center space-x-4 mb-4">
            <FileText className="w-12 h-12 text-purple-600" />
            <h1 className="text-5xl font-bold text-gray-900">CV One Pager Generator</h1>
          </div>
          <p className="text-xl text-gray-600 ml-16">Upload a CV in PDF format</p>
        </div>

        {/* Upload Area */}
        {!uploadedFile && !isProcessing && (
          <div className="bg-white rounded-2xl shadow-xl p-12">
            <div
              onDragEnter={handleDragEnter}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={`border-3 border-dashed rounded-xl p-16 text-center transition-all ${
                isDragging
                  ? 'border-purple-600 bg-purple-50'
                  : 'border-gray-300 bg-gray-50 hover:bg-gray-100'
              }`}
            >
              <div className="flex flex-col items-center space-y-6">
                <div className={`p-6 rounded-full ${isDragging ? 'bg-purple-100' : 'bg-purple-50'}`}>
                  <Upload className={`w-16 h-16 ${isDragging ? 'text-purple-600' : 'text-purple-400'}`} />
                </div>
                
                <div>
                  <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                    Drag and drop file here
                  </h3>
                  <p className="text-gray-500 text-lg">
                    Limit 200MB per file • PDF
                  </p>
                </div>

                <div className="relative">
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handleFileInput}
                    className="hidden"
                    id="file-input"
                  />
                  <label
                    htmlFor="file-input"
                    className="cursor-pointer inline-block bg-purple-600 hover:bg-purple-700 text-white font-semibold py-4 px-10 rounded-lg transition-colors text-lg"
                  >
                    Browse files
                  </label>
                </div>
              </div>
            </div>

            {error && (
              <div className="mt-6 bg-red-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-xl flex items-start space-x-3">
                <X className="w-6 h-6 flex-shrink-0 mt-0.5" />
                <span className="text-lg">{error}</span>
              </div>
            )}
          </div>
        )}

        {/* Processing State */}
        {isProcessing && (
          <div className="bg-white rounded-2xl shadow-xl p-16">
            <div className="flex flex-col items-center space-y-6">
              <Loader2 className="w-20 h-20 text-purple-600 animate-spin" />
              <div className="text-center">
                <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                  Processing your CV...
                </h3>
                <p className="text-gray-600 text-lg">
                  Generating your one-pager document
                </p>
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
                <h3 className="text-3xl font-semibold text-gray-900 mb-3">
                  One-Pager Generated Successfully!
                </h3>
                <p className="text-gray-600 text-lg mb-2">
                  File: <span className="font-medium">{uploadedFile.name}</span>
                </p>
                <p className="text-gray-500">
                  Size: {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
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
        <p className="text-sm">
          Powered by Accenture • Confidential and secure processing
        </p>
      </footer>
    </div>
  );
}
