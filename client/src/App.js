import React, { useState, useMemo, useEffect } from 'react';
import axios from 'axios';
import { ArrowPathIcon, CloudArrowDownIcon, ChartBarIcon, TableCellsIcon, BeakerIcon, CpuChipIcon } from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { motion } from 'framer-motion';
import youtubeLogo from './assets/youtube_logo.png';
import backgroundVideo from './assets/background_video.mp4';
import MLDashboard from './components/MLDashboard';
import { API_BASE_URL } from './config';

function App() {
  const [url, setUrl] = useState('');
  const [comments, setComments] = useState([]);
  const [rawComments, setRawComments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzingLoading, setAnalyzingLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');
  const [selectedSentiment, setSelectedSentiment] = useState('all');
  const [viewMode, setViewMode] = useState('chart'); // 'chart', 'table', or 'ml'
  const [stats, setStats] = useState(null);
  const [sentimentMethod, setSentimentMethod] = useState('textblob'); // 'textblob' or 'transformer'
  const [selectedModel, setSelectedModel] = useState('');
  const [availableModels, setAvailableModels] = useState([]);
  const [commentsAnalyzed, setCommentsAnalyzed] = useState(false);
  const [demoMode, setDemoMode] = useState(false);
  const [apiStatus, setApiStatus] = useState(null);
  const [maxComments, setMaxComments] = useState(200);
  const [maxPages, setMaxPages] = useState(5);

  // Fetch available models and API status on component mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/ml/models`);
        setAvailableModels(response.data.models);
        if (response.data.models.length > 0) {
          setSelectedModel(response.data.models[0]);
        }
      } catch (err) {
        console.error('Failed to fetch models:', err);
      }
    };

    const fetchApiStatus = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/status`);
        setApiStatus(response.data);
      } catch (err) {
        console.error('Failed to fetch API status:', err);
      }
    };

    fetchModels();
    fetchApiStatus();
  }, []);

  const sentimentStats = useMemo(() => {
    const stats = {
      positive: 0,
      neutral: 0,
      negative: 0,
      total: comments.length
    };

    comments.forEach(comment => {
      stats[comment.sentiment.toLowerCase()]++;
    });

    return stats;
  }, [comments]);

  const chartData = useMemo(() => [
    { name: 'Positive', value: sentimentStats.positive, color: '#10B981' },
    { name: 'Neutral', value: sentimentStats.neutral, color: '#6B7280' },
    { name: 'Negative', value: sentimentStats.negative, color: '#EF4444' }
  ], [sentimentStats]);

  const filteredComments = useMemo(() => {
    if (selectedSentiment === 'all') return comments;
    return comments.filter(comment => 
      comment.sentiment.toLowerCase() === selectedSentiment
    );
  }, [comments, selectedSentiment]);

  const fetchComments = async (forceDemo = false) => {
    if (!url && !forceDemo) {
      setError('Please enter a YouTube URL.');
      return;
    }
    setLoading(true);
    setError('');
    setCommentsAnalyzed(false);
    setDemoMode(forceDemo);
    
    try {
      let response;
      if (forceDemo) {
        // Use demo endpoint
        response = await axios.get(`${API_BASE_URL}/demo/comments?max_comments=50&category=tech`);
      } else {
        // Fetch raw comments without sentiment analysis
        response = await axios.get(`${API_BASE_URL}/comments/raw?url=${encodeURIComponent(url)}&max_comments=${maxComments}&max_pages=${maxPages}&use_demo=${demoMode}`);
      }
      
      setRawComments(response.data.comments);
      setComments([]); // Clear analyzed comments
      setStats(response.data.stats);
      
      // Check if we got demo data due to quota exceeded
      if (response.data.stats.demo_fallback || response.data.stats.warning) {
        setDemoMode(true);
        setError(response.data.stats.warning || 'Using demo data due to API limitations');
      }
      
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Could not fetch comments. Please check the URL and try again.';
      
      // If quota exceeded, try demo mode
      if (err.response?.status === 429 || errorMessage.includes('quota')) {
        try {
          const demoResponse = await axios.get(`${API_BASE_URL}/demo/comments?max_comments=50&category=tech`);
          setRawComments(demoResponse.data.comments);
          setComments([]);
          setStats(demoResponse.data.stats);
          setDemoMode(true);
          setError('YouTube API quota exceeded. Showing demo data instead. Please try again later or add more API keys.');
        } catch (demoErr) {
          setError('Failed to fetch comments and demo data is unavailable.');
          setRawComments([]);
          setComments([]);
          setStats(null);
        }
      } else {
        setError(errorMessage);
        setRawComments([]);
        setComments([]);
        setStats(null);
      }
    } finally {
      setLoading(false);
    }
  };

  const tryDemoMode = () => {
    fetchComments(true);
  };

  const analyzeSentiment = async () => {
    if (rawComments.length === 0) {
      setError('No comments to analyze. Please fetch comments first.');
      return;
    }
    
    if (sentimentMethod === 'transformer' && !selectedModel) {
      setError('Please select a model for transformer analysis.');
      return;
    }

    setAnalyzingLoading(true);
    setError('');
    try {
      const response = await axios.post(`${API_BASE_URL}/analyze_sentiment`, {
        comments: rawComments,
        method: sentimentMethod,
        model_name: sentimentMethod === 'transformer' ? selectedModel : null
      });
      
      setComments(response.data.comments);
      setStats(prevStats => ({
        ...prevStats,
        ...response.data.stats
      }));
      setCommentsAnalyzed(true);
      
      // Analiz tamamlandıktan sonra otomatik olarak chart view'a geç
      setViewMode('chart');
      
      // Sonuçlara scroll et (kısa bir delay ile)
      setTimeout(() => {
        const resultsElement = document.querySelector('[data-scroll-target="results"]');
        if (resultsElement) {
          resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not analyze sentiment. Please try again.');
    } finally {
      setAnalyzingLoading(false);
    }
  };

  const downloadCSV = async () => {
    if (!url) {
      setError('Please enter a YouTube URL.');
      return;
    }
    setDownloading(true);
    try {
      const commentsToExport = selectedSentiment === 'all' ? comments : filteredComments;
      const csvContent = [
        ['Comment', 'Sentiment', 'Timestamp'],
        ...commentsToExport.map(comment => [
          `"${comment.comment.replace(/"/g, '""')}"`,
          comment.sentiment,
          comment.timestamp || ''
        ])
      ].map(row => row.join(',')).join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const urlBlob = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = urlBlob;
      link.setAttribute('download', `youtube_comments_${selectedSentiment}.csv`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      setError('Failed to download CSV.');
    } finally {
      setDownloading(false);
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment.toLowerCase()) {
      case 'positive':
        return 'bg-green-100 text-green-700 border-green-300';
      case 'negative':
        return 'bg-red-100 text-red-700 border-red-300';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-300';
    }
  };

  const SentimentCard = ({ label, count, color }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`p-4 rounded-xl shadow-sm border ${color} flex flex-col items-center`}
    >
      <span className="text-2xl font-bold">{count}</span>
      <span className="text-sm font-medium">{label}</span>
    </motion.div>
  );

  const ChartView = () => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h2 className="text-xl font-semibold mb-4 text-gray-900 flex items-center">
        <ChartBarIcon className="h-6 w-6 mr-2 text-red-500" />
        Sentiment Distribution
      </h2>
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              outerRadius={120}
              fill="#8884d8"
              dataKey="value"
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip 
              formatter={(value, name) => [`${value} (${((value / sentimentStats.total) * 100).toFixed(1)}%)`, name]}
            />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );

  const TableView = () => (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h2 className="text-xl font-semibold mb-4 text-gray-900 flex items-center">
        <TableCellsIcon className="h-6 w-6 mr-2 text-red-500" />
        Comments Table
      </h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Comment</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sentiment</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Timestamp</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredComments.map((comment, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-pre-line">{comment.comment}</td>
                <td className="px-6 py-4">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getSentimentColor(comment.sentiment)}`}>
                    {comment.sentiment}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  {comment.timestamp || 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-red-50 via-blue-50 to-purple-50">
      {/* Video Background */}
      <div className="absolute inset-0 z-0">
        {/* Colorful gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 via-blue-500/10 to-purple-500/10 mix-blend-overlay z-20" />
        {/* Video container with reduced opacity */}
        <div className="absolute inset-0 bg-white/5 z-10" />
        <video
          autoPlay
          loop
          muted
          className="w-full h-full object-cover opacity-75"
        >
          <source src={backgroundVideo} type="video/mp4" />
        </video>
      </div>

      <div className="relative z-10 py-8 flex flex-col justify-center sm:py-16">
        <div className="relative px-4 py-10 sm:max-w-4xl md:max-w-6xl mx-auto">
          <div className="bg-white/85 backdrop-blur-sm shadow-xl rounded-3xl p-8 animate-fadeIn">
            <div className="max-w-4xl mx-auto">
              {/* YouTube Logo */}
              <div className="flex justify-center mb-8">
                <div className="bg-red-500 rounded-2xl p-4 inline-flex items-center shadow-md">
                  <img src={youtubeLogo} alt="YouTube Logo" className="w-40 h-auto object-contain" />
                </div>
              </div>

              <h1 className="text-3xl font-bold text-center mb-8 text-gray-900">YouTube Comments Analyzer</h1>

              {/* API Status and Demo Mode Indicators */}
              {(demoMode || apiStatus) && (
                <div className="mb-6 space-y-2">
                  {demoMode && (
                    <div className="bg-yellow-100 border border-yellow-300 text-yellow-800 px-4 py-3 rounded-lg text-sm">
                      <div className="flex items-center">
                        <span className="mr-2">⚠️</span>
                        <strong>Demo Mode Active:</strong> Showing sample data due to API limitations.
                      </div>
                    </div>
                  )}
                  {apiStatus && (
                    <div className="bg-blue-100 border border-blue-300 text-blue-800 px-4 py-3 rounded-lg text-sm">
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="mr-2">🔑</span>
                          <strong>API Status:</strong> {apiStatus.api_keys_configured} key(s) configured, 
                          using key {apiStatus.current_api_key}
                        </div>
                        <div className="text-xs">
                          {apiStatus.quota_management === 'enabled' ? '✅ Quota rotation enabled' : '⚠️ Single key only'}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* URL Input Section */}
              <div className="flex flex-col space-y-4">
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter YouTube video URL"
                  className="px-6 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-400 text-gray-900 placeholder-gray-400 shadow-sm transition-all duration-200"
                />
                
                {/* Comment Limits Controls */}
                <div className="flex gap-4 items-center bg-gray-50 p-4 rounded-xl">
                  <div className="flex items-center space-x-2">
                    <label className="text-sm font-medium text-gray-700">Max Comments:</label>
                    <select
                      value={maxComments}
                      onChange={(e) => setMaxComments(parseInt(e.target.value))}
                      className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                    >
                      <option value={50}>50</option>
                      <option value={100}>100</option>
                      <option value={200}>200</option>
                      <option value={500}>500</option>
                      <option value={1000}>1000</option>
                    </select>
                  </div>
                  <div className="flex items-center space-x-2">
                    <label className="text-sm font-medium text-gray-700">Max Pages:</label>
                    <select
                      value={maxPages}
                      onChange={(e) => setMaxPages(parseInt(e.target.value))}
                      className="border border-gray-300 rounded-md px-3 py-1 text-sm"
                    >
                      <option value={1}>1</option>
                      <option value={3}>3</option>
                      <option value={5}>5</option>
                      <option value={10}>10</option>
                    </select>
                  </div>
                  <div className="text-xs text-gray-500">
                    ~{maxComments} comments, {maxPages} API calls
                  </div>
                </div>

                <div className="flex gap-4">
                  <button
                    onClick={() => fetchComments(false)}
                    disabled={loading}
                    className="flex-1 px-6 py-3 bg-red-500 text-white rounded-xl hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-400 disabled:opacity-50 transition-all duration-300 shadow-md"
                  >
                    {loading ? (
                      <div className="flex items-center justify-center">
                        <ArrowPathIcon className="h-5 w-5 animate-spin mr-2" />
                        Loading...
                      </div>
                    ) : (
                      'Fetch Comments'
                    )}
                  </button>
                  <button
                    onClick={tryDemoMode}
                    disabled={loading}
                    className="px-6 py-3 bg-yellow-500 text-white rounded-xl hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-400 disabled:opacity-50 transition-all duration-300 shadow-md"
                  >
                    Try Demo
                  </button>
                  {comments.length > 0 && (
                    <button
                      onClick={downloadCSV}
                      disabled={downloading}
                      className="px-6 py-3 bg-blue-100 text-blue-700 rounded-xl hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-300 disabled:opacity-50 transition-all duration-300 flex items-center border border-blue-200 shadow-sm"
                    >
                      {downloading ? (
                        <ArrowPathIcon className="h-5 w-5 animate-spin" />
                      ) : (
                        <CloudArrowDownIcon className="h-5 w-5" />
                      )}
                    </button>
                  )}
                </div>
              </div>

              {error && (
                <div className="mt-4 text-red-500 text-sm text-center animate-fadeIn">
                  {error}
                </div>
              )}

              {/* Sentiment Analysis Controls - Show after raw comments are fetched */}
              {rawComments.length > 0 && !commentsAnalyzed && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-8 bg-white p-6 rounded-xl shadow-sm border border-gray-100"
                >
                  <h2 className="text-xl font-semibold mb-4 text-gray-900 flex items-center">
                    <BeakerIcon className="h-6 w-6 mr-2 text-purple-500" />
                    Sentiment Analysis
                  </h2>
                  <p className="text-gray-600 mb-4">
                    {rawComments.length} comments fetched successfully! Now choose how to analyze their sentiment:
                  </p>
                  
                  <div className="space-y-4">
                    {/* Method Selection */}
                    <div className="flex items-center space-x-6">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="textblob"
                          checked={sentimentMethod === 'textblob'}
                          onChange={(e) => setSentimentMethod(e.target.value)}
                          className="mr-2"
                        />
                        <span className="text-sm font-medium">TextBlob (Fast & Simple)</span>
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="transformer"
                          checked={sentimentMethod === 'transformer'}
                          onChange={(e) => setSentimentMethod(e.target.value)}
                          className="mr-2"
                        />
                        <span className="text-sm font-medium">Transformer Models (Accurate)</span>
                      </label>
                    </div>

                    {/* Model Selection for Transformer */}
                    {sentimentMethod === 'transformer' && (
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

                    {/* Analyze Button */}
                    <button
                      onClick={analyzeSentiment}
                      disabled={analyzingLoading}
                      className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-xl text-sm font-medium flex items-center transition-all duration-300"
                    >
                      {analyzingLoading ? (
                        <>
                          <ArrowPathIcon className="h-5 w-5 animate-spin mr-2" />
                          Analyzing Sentiment...
                        </>
                      ) : (
                        <>
                          <BeakerIcon className="h-5 w-5 mr-2" />
                          Analyze Sentiment
                        </>
                      )}
                    </button>
                  </div>
                </motion.div>
              )}

              {/* Stats Section */}
              {stats && (
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                  <h2 className="text-xl font-semibold mb-4 text-gray-900 flex items-center">
                    <span className="mr-2">📊</span>
                    Comments Statistics
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-700">{rawComments.length}</div>
                      <div className="text-sm text-blue-600">Total Comments Fetched</div>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-700">{stats.pages_processed}</div>
                      <div className="text-sm text-purple-600">Pages Processed</div>
                    </div>
                  </div>
                  {demoMode && (
                    <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                      <div className="text-sm text-yellow-800">
                        <strong>Demo Mode:</strong> Showing sample data for demonstration purposes
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Sentiment Summary Cards - Only show if comments are analyzed */}
              {comments.length > 0 && commentsAnalyzed && (
                <div data-scroll-target="results" className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                  <h2 className="text-xl font-semibold mb-4 text-gray-900 flex items-center">
                    <span className="mr-2">🎯</span>
                    Sentiment Analysis Results
                    <span className="ml-2 text-sm font-normal text-gray-500">
                      ({sentimentMethod === 'transformer' ? `${selectedModel}` : 'TextBlob'})
                    </span>
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <SentimentCard
                      label="Total Analyzed"
                      count={sentimentStats.total}
                      color="bg-blue-100 text-blue-700 border-blue-300"
                    />
                    <SentimentCard
                      label="Positive"
                      count={sentimentStats.positive}
                      color="bg-green-100 text-green-700 border-green-300"
                    />
                    <SentimentCard
                      label="Neutral"
                      count={sentimentStats.neutral}
                      color="bg-gray-100 text-gray-700 border-gray-300"
                    />
                    <SentimentCard
                      label="Negative"
                      count={sentimentStats.negative}
                      color="bg-red-100 text-red-700 border-red-300"
                    />
                  </div>
                </div>
              )}

              {/* Raw Comments Info - Show if comments fetched but not analyzed */}
              {rawComments.length > 0 && !commentsAnalyzed && (
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                  <h2 className="text-xl font-semibold mb-4 text-gray-900 flex items-center">
                    <span className="mr-2">📝</span>
                    Raw Comments Fetched
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <SentimentCard
                      label="Comments Ready for Analysis"
                      count={rawComments.length}
                      color="bg-blue-100 text-blue-700 border-blue-300"
                    />
                    <div className="p-4 bg-yellow-50 rounded-xl border border-yellow-300 flex flex-col items-center">
                      <span className="text-2xl font-bold text-yellow-700">⏳</span>
                      <span className="text-sm font-medium text-yellow-700">Waiting for Analysis</span>
                    </div>
                  </div>
                  <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="text-sm text-blue-800">
                      <strong>Next Step:</strong> Choose a sentiment analysis method below to analyze these comments
                    </div>
                  </div>
                </div>
              )}

              {/* View Toggle and Content - Only show when comments are analyzed */}
              {comments.length > 0 && commentsAnalyzed && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-6"
                >
                  {/* View Toggle */}
                  <div className="flex justify-end mb-4">
                    <div className="inline-flex rounded-md shadow-sm">
                      <button
                        onClick={() => setViewMode('chart')}
                        className={`px-4 py-2 text-sm font-medium rounded-l-md ${
                          viewMode === 'chart'
                            ? 'bg-red-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <ChartBarIcon className="h-5 w-5 inline-block mr-2" />
                        Chart View
                      </button>
                      <button
                        onClick={() => setViewMode('table')}
                        className={`px-4 py-2 text-sm font-medium ${
                          viewMode === 'table'
                            ? 'bg-red-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <TableCellsIcon className="h-5 w-5 inline-block mr-2" />
                        Table View
                      </button>
                      <button
                        onClick={() => setViewMode('ml')}
                        className={`px-4 py-2 text-sm font-medium rounded-r-md ${
                          viewMode === 'ml'
                            ? 'bg-red-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <BeakerIcon className="h-5 w-5 inline-block mr-2" />
                        ML Analysis
                      </button>
                    </div>
                  </div>

                  {/* Dynamic View Content */}
                  {viewMode === 'chart' && <ChartView />}
                  {viewMode === 'table' && <TableView />}
                  {viewMode === 'ml' && <MLDashboard 
                    comments={comments} 
                    initialSentimentMethod={'textblob'}
                    initialSelectedModel={''}
                    onAnalysisComplete={(newComments) => {
                      setComments(newComments);
                      // Stats'ı da güncelle
                      const sentimentCounts = {"Positive": 0, "Neutral": 0, "Negative": 0};
                      newComments.forEach(comment => {
                        const sentiment = comment.sentiment.charAt(0).toUpperCase() + comment.sentiment.slice(1);
                        sentimentCounts[sentiment]++;
                      });
                      setStats(prevStats => ({
                        ...prevStats,
                        sentiment_distribution: sentimentCounts,
                        method_used: 'ml_analysis'
                      }));
                      
                      // ML analizi tamamlandıktan sonra chart view'a geç
                      setTimeout(() => {
                        setViewMode('chart');
                        // Sonuçlara scroll et
                        const resultsElement = document.querySelector('[data-scroll-target="results"]');
                        if (resultsElement) {
                          resultsElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }
                      }, 500);
                    }}
                  />}
                </motion.div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;