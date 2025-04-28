import React, { useState, useMemo } from 'react';
import axios from 'axios';
import { ArrowPathIcon, CloudArrowDownIcon, ChartBarIcon, TableCellsIcon } from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { motion } from 'framer-motion';
import youtubeLogo from './assets/youtube_logo.png';
import backgroundVideo from './assets/background_video.mp4';

function App() {
  const [url, setUrl] = useState('');
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');
  const [selectedSentiment, setSelectedSentiment] = useState('all');
  const [viewMode, setViewMode] = useState('chart'); // 'chart' or 'table'
  const [stats, setStats] = useState(null);

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

  const fetchComments = async () => {
    if (!url) {
      setError('Please enter a YouTube URL.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`http://localhost:8000/comments?url=${encodeURIComponent(url)}`);
      setComments(response.data.comments);
      setStats(response.data.stats);
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not fetch comments. Please check the URL and try again.');
      setComments([]);
      setStats(null);
    } finally {
      setLoading(false);
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

              {/* URL Input Section */}
              <div className="flex flex-col space-y-4">
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter YouTube video URL"
                  className="px-6 py-3 bg-white border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-400 text-gray-900 placeholder-gray-400 shadow-sm transition-all duration-200"
                />
                <div className="flex gap-4">
                  <button
                    onClick={fetchComments}
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

              {comments.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-8 space-y-8"
                >
                  {/* Stats Section */}
                  {stats && (
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                      <h2 className="text-xl font-semibold mb-4 text-gray-900 flex items-center">
                        <span className="mr-2">📊</span>
                        Comments Statistics
                      </h2>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="p-4 bg-blue-50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-700">{stats.total_comments}</div>
                          <div className="text-sm text-blue-600">Total Comments</div>
                        </div>
                        <div className="p-4 bg-purple-50 rounded-lg">
                          <div className="text-2xl font-bold text-purple-700">{stats.pages_processed}</div>
                          <div className="text-sm text-purple-600">Pages Processed</div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Sentiment Summary Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <SentimentCard
                      label="Total Comments"
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
                        className={`px-4 py-2 text-sm font-medium rounded-r-md ${
                          viewMode === 'table'
                            ? 'bg-red-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <TableCellsIcon className="h-5 w-5 inline-block mr-2" />
                        Table View
                      </button>
                    </div>
                  </div>

                  {/* Dynamic View Content */}
                  {viewMode === 'chart' ? <ChartView /> : <TableView />}

                  {/* Comment List with Filter */}
                  <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                    <div className="flex justify-between items-center mb-4">
                      <h2 className="text-xl font-semibold text-gray-900">Comments</h2>
                      <div className="flex gap-2">
                        <button
                          onClick={() => setSelectedSentiment('all')}
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            selectedSentiment === 'all'
                              ? 'bg-red-500 text-white'
                              : 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          All
                        </button>
                        <button
                          onClick={() => setSelectedSentiment('positive')}
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            selectedSentiment === 'positive'
                              ? 'bg-green-500 text-white'
                              : 'bg-green-100 text-green-700'
                          }`}
                        >
                          Positive
                        </button>
                        <button
                          onClick={() => setSelectedSentiment('neutral')}
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            selectedSentiment === 'neutral'
                              ? 'bg-gray-500 text-white'
                              : 'bg-gray-100 text-gray-700'
                          }`}
                        >
                          Neutral
                        </button>
                        <button
                          onClick={() => setSelectedSentiment('negative')}
                          className={`px-3 py-1 rounded-full text-sm font-medium ${
                            selectedSentiment === 'negative'
                              ? 'bg-red-500 text-white'
                              : 'bg-red-100 text-red-700'
                          }`}
                        >
                          Negative
                        </button>
                      </div>
                    </div>
                    <div className="space-y-4 max-h-96 overflow-y-auto custom-scrollbar pr-2">
                      {filteredComments.map((comment, index) => (
                        <motion.div
                          key={index}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="p-4 bg-white border border-gray-100 rounded-xl shadow-sm transition-all duration-300 hover:shadow-lg"
                        >
                          <div className="flex flex-col gap-2">
                            <div className="flex justify-between items-start gap-4">
                              <p className="text-gray-800 flex-1 whitespace-pre-line">{comment.comment}</p>
                              <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getSentimentColor(comment.sentiment)}`}>
                                {comment.sentiment}
                              </span>
                            </div>
                            <div className="flex items-center justify-between text-sm text-gray-500">
                              <div className="flex items-center gap-4">
                                <div className="flex items-center">
                                  <span className="mr-2">👤</span>
                                  {comment.author}
                                </div>
                                {comment.likes > 0 && (
                                  <div className="flex items-center">
                                    <span className="mr-2">👍</span>
                                    {comment.likes}
                                  </div>
                                )}
                              </div>
                              <div>
                                {new Date(comment.timestamp).toLocaleDateString()} {new Date(comment.timestamp).toLocaleTimeString()}
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
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