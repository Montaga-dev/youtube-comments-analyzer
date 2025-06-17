import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { BeakerIcon, CpuChipIcon, SparklesIcon } from '@heroicons/react/24/outline';

const MLDashboard = ({ comments, initialSentimentMethod = 'textblob', initialSelectedModel = '', onAnalysisComplete }) => {
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('');
  const [useTransformer, setUseTransformer] = useState(false);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Sadece bir kez initialize etmek için ref kullan
  const initialized = useRef(false);

  useEffect(() => {
    fetchAvailableModels();
  }, []);

  // Sadece ilk kez modeller yüklendiğinde initial değerleri set et
  useEffect(() => {
    if (!initialized.current && availableModels.length > 0) {
      // Initial method set et
      setUseTransformer(initialSentimentMethod === 'transformer');
      
      // Initial model set et
      if (initialSelectedModel && availableModels.includes(initialSelectedModel)) {
        setSelectedModel(initialSelectedModel);
      } else if (availableModels.length > 0) {
        setSelectedModel(availableModels[0]);
      }
      
      initialized.current = true;
    }
  }, [availableModels]);

  const fetchAvailableModels = async () => {
    try {
      const response = await fetch('http://localhost:8000/ml/models');
      const data = await response.json();
      setAvailableModels(data.models);
    } catch (err) {
      console.error('Failed to fetch models:', err);
    }
  };

  const analyzeComments = async () => {
    if (!comments || comments.length === 0) {
      setError('No comments to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const texts = comments.map(comment => comment.comment);
      const response = await fetch('http://localhost:8000/ml/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          texts: texts,
          use_transformer: useTransformer,
          model_name: useTransformer ? selectedModel : null
        }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();
      setResults(data);
      
      // Ana component'teki comments'ı güncelle
      if (onAnalysisComplete && data.results) {
        const updatedComments = data.results.map((result, index) => ({
          ...comments[index], // Mevcut comment bilgilerini koru
          sentiment: result.sentiment.charAt(0).toUpperCase() + result.sentiment.slice(1), // İlk harfi büyük yap
          confidence: result.sentiment_confidence,
          method: result.sentiment_method
        }));
        onAnalysisComplete(updatedComments);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'text-green-600 bg-green-100';
      case 'negative':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h2 className="text-xl font-semibold mb-4 text-gray-900 flex items-center">
        <BeakerIcon className="h-6 w-6 mr-2 text-purple-500" />
        ML Sentiment Analysis
      </h2>

      {/* Model Selection */}
      <div className="mb-6 space-y-4">
        <div className="flex items-center space-x-4">
          <label className="flex items-center">
            <input
              type="radio"
              checked={!useTransformer}
              onChange={() => setUseTransformer(false)}
              className="mr-2"
            />
            <span className="text-sm font-medium">TextBlob (Fast)</span>
          </label>
          <label className="flex items-center">
            <input
              type="radio"
              checked={useTransformer}
              onChange={() => setUseTransformer(true)}
              className="mr-2"
            />
            <span className="text-sm font-medium">Transformer Models (Accurate)</span>
          </label>
        </div>

        {useTransformer && (
          <div className="flex items-center space-x-4">
            <CpuChipIcon className="h-5 w-5 text-blue-500" />
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm"
            >
              {availableModels.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </select>
          </div>
        )}

        <button
          onClick={analyzeComments}
          disabled={loading || !comments || comments.length === 0}
          className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md text-sm font-medium flex items-center"
        >
          {loading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Analyzing...
            </>
          ) : (
            <>
              <SparklesIcon className="h-4 w-4 mr-2" />
              Analyze with ML
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {results && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          <h3 className="text-lg font-semibold text-gray-900">Analysis Results</h3>
          
          {/* Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {results.summary.sentiment_distribution.positive}
              </div>
              <div className="text-sm text-green-600">Positive</div>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-gray-600">
                {results.summary.sentiment_distribution.neutral}
              </div>
              <div className="text-sm text-gray-600">Neutral</div>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {results.summary.sentiment_distribution.negative}
              </div>
              <div className="text-sm text-red-600">Negative</div>
            </div>
          </div>

          {/* Sample Results */}
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Sample Analysis Results:</h4>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {results.results.slice(0, 10).map((result, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-3">
                  <div className="text-sm text-gray-800 mb-2">{result.text}</div>
                  <div className="flex items-center justify-between">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSentimentColor(result.sentiment)}`}>
                      {result.sentiment}
                    </span>
                    <span className="text-xs text-gray-500">
                      Confidence: {(result.sentiment_confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="text-xs text-gray-400 mt-1">
                    Method: {result.sentiment_method}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default MLDashboard; 