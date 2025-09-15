import React, { useState, useEffect } from 'react';
import './App.css';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [clusters, setClusters] = useState([]);
  const [dashboardData, setDashboardData] = useState(null);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);

  useEffect(() => {
    fetchDashboardData();
    fetchClusters();
    fetchAlerts();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_URL}/api/dashboard/overview`);
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  const fetchClusters = async () => {
    try {
      const response = await fetch(`${API_URL}/api/clusters`);
      const data = await response.json();
      setClusters(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching clusters:', error);
      setLoading(false);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch(`${API_URL}/api/alerts`);
      const data = await response.json();
      setAlerts(data);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  const analyzeCluster = async (clusterId) => {
    setLoadingAnalysis(true);
    try {
      const response = await fetch(`${API_URL}/api/clusters/${clusterId}/analyze`, {
        method: 'POST'
      });
      const analysisData = await response.json();
      setAnalysis(analysisData);
      
      // Fetch recommendations
      const recResponse = await fetch(`${API_URL}/api/clusters/${clusterId}/recommendations`);
      const recData = await recResponse.json();
      setRecommendations(recData);
    } catch (error) {
      console.error('Error analyzing cluster:', error);
    }
    setLoadingAnalysis(false);
  };

  const resolveAlert = async (alertId) => {
    try {
      await fetch(`${API_URL}/api/alerts/${alertId}/resolve`, {
        method: 'POST'
      });
      fetchAlerts(); // Refresh alerts
    } catch (error) {
      console.error('Error resolving alert:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-3xl font-bold text-gray-900">KubeCost</h1>
                <p className="text-sm text-gray-600">AI-Powered Kubernetes Cost Optimization</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex bg-gray-100 rounded-lg p-1">
                <button
                  onClick={() => setActiveTab('dashboard')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'dashboard' 
                      ? 'bg-white text-blue-600 shadow-sm' 
                      : 'text-gray-700 hover:text-gray-900'
                  }`}
                >
                  Dashboard
                </button>
                <button
                  onClick={() => setActiveTab('clusters')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'clusters' 
                      ? 'bg-white text-blue-600 shadow-sm' 
                      : 'text-gray-700 hover:text-gray-900'
                  }`}
                >
                  Clusters
                </button>
                <button
                  onClick={() => setActiveTab('analysis')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    activeTab === 'analysis' 
                      ? 'bg-white text-blue-600 shadow-sm' 
                      : 'text-gray-700 hover:text-gray-900'
                  }`}
                >
                  AI Analysis
                </button>
                <button
                  onClick={() => setActiveTab('alerts')}
                  className={`px-4 py-2 rounded-md text-sm font-medium transition-colors relative ${
                    activeTab === 'alerts' 
                      ? 'bg-white text-blue-600 shadow-sm' 
                      : 'text-gray-700 hover:text-gray-900'
                  }`}
                >
                  Alerts
                  {alerts.filter(alert => !alert.resolved).length > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                      {alerts.filter(alert => !alert.resolved).length}
                    </span>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      {activeTab === 'dashboard' && (
        <div className="relative bg-gradient-to-r from-blue-600 to-purple-700 text-white">
          <div className="absolute inset-0">
            <img 
              src="https://images.unsplash.com/photo-1690627931320-16ac56eb2588" 
              alt="Cloud Infrastructure" 
              className="w-full h-full object-cover opacity-20"
            />
          </div>
          <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
            <div className="text-center">
              <h2 className="text-4xl font-bold mb-4">
                Optimize Your Kubernetes Costs with AI
              </h2>
              <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
                Reduce cloud spending by up to 60% with intelligent cost analysis, 
                automated recommendations, and real-time monitoring.
              </p>
              <div className="flex justify-center space-x-4">
                <button 
                  onClick={() => setActiveTab('clusters')}
                  className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  View Clusters
                </button>
                <button 
                  onClick={() => setActiveTab('analysis')}
                  className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors"
                >
                  AI Analysis
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && dashboardData && (
          <div className="space-y-8">
            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                      </svg>
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900">Total Clusters</p>
                    <p className="text-2xl font-bold text-gray-900">{dashboardData.total_clusters}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900">Monthly Cost</p>
                    <p className="text-2xl font-bold text-gray-900">${dashboardData.total_monthly_cost}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900">Potential Savings</p>
                    <p className="text-2xl font-bold text-green-600">${dashboardData.potential_savings}</p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-yellow-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                      </svg>
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-900">Active Alerts</p>
                    <p className="text-2xl font-bold text-gray-900">{dashboardData.alerts_count}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Utilization Chart */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Resource Utilization</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">CPU Utilization</span>
                    <span className="text-sm text-gray-900">{dashboardData.avg_cpu_utilization}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${dashboardData.avg_cpu_utilization}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">Memory Utilization</span>
                    <span className="text-sm text-gray-900">{dashboardData.avg_memory_utilization}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-purple-600 h-2 rounded-full" 
                      style={{ width: `${dashboardData.avg_memory_utilization}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Cost Trends */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Trends (Last 7 Days)</h3>
              <div className="flex items-end space-x-2 h-32">
                {dashboardData.cost_trends.map((trend, index) => (
                  <div key={index} className="flex-1 flex flex-col items-center">
                    <div 
                      className="w-full bg-blue-500 rounded-t"
                      style={{ 
                        height: `${(trend.cost / Math.max(...dashboardData.cost_trends.map(t => t.cost))) * 100}%`,
                        minHeight: '10px'
                      }}
                    ></div>
                    <span className="text-xs text-gray-600 mt-2">
                      {new Date(trend.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Clusters Tab */}
        {activeTab === 'clusters' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Kubernetes Clusters</h2>
              <span className="text-sm text-gray-600">{clusters.length} clusters found</span>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {clusters.map((cluster) => (
                <div key={cluster.id} className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-lg transition-shadow">
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900">{cluster.name}</h3>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        cluster.provider === 'AWS' ? 'bg-orange-100 text-orange-800' :
                        cluster.provider === 'GCP' ? 'bg-blue-100 text-blue-800' :
                        'bg-purple-100 text-purple-800'
                      }`}>
                        {cluster.provider}
                      </span>
                    </div>
                    
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Region</span>
                        <span className="text-sm font-medium text-gray-900">{cluster.region}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Nodes</span>
                        <span className="text-sm font-medium text-gray-900">{cluster.nodes.length}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Monthly Cost</span>
                        <span className="text-sm font-bold text-green-600">${cluster.total_cost.toFixed(2)}</span>
                      </div>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <button
                        onClick={() => {
                          setSelectedCluster(cluster);
                          setActiveTab('analysis');
                          analyzeCluster(cluster.id);
                        }}
                        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                      >
                        Analyze Cluster
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analysis Tab */}
        {activeTab === 'analysis' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">AI-Powered Cost Analysis</h2>
              {selectedCluster && (
                <div className="text-sm text-gray-600">
                  Analyzing: <span className="font-medium">{selectedCluster.name}</span>
                </div>
              )}
            </div>

            {!selectedCluster && (
              <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-200">
                <img 
                  src="https://images.unsplash.com/photo-1659479749984-d48333116052" 
                  alt="Analytics Dashboard" 
                  className="w-32 h-32 mx-auto mb-4 rounded-lg opacity-50"
                />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Cluster to Analyze</h3>
                <p className="text-gray-600 mb-4">Choose a cluster from the Clusters tab to get AI-powered cost optimization insights.</p>
                <button
                  onClick={() => setActiveTab('clusters')}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  View Clusters
                </button>
              </div>
            )}

            {loadingAnalysis && (
              <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-200">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">AI Analysis in Progress</h3>
                <p className="text-gray-600">Our AI is analyzing your cluster for cost optimization opportunities...</p>
              </div>
            )}

            {analysis && selectedCluster && (
              <div className="space-y-6">
                {/* Analysis Overview */}
                <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Analysis Results</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">${analysis.potential_savings.toFixed(2)}</div>
                      <div className="text-sm text-green-700">Potential Monthly Savings</div>
                    </div>
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">{analysis.confidence_score.toFixed(1)}%</div>
                      <div className="text-sm text-blue-700">Confidence Score</div>
                    </div>
                    <div className="text-center p-4 bg-purple-50 rounded-lg">
                      <div className="text-2xl font-bold text-purple-600">{recommendations.length}</div>
                      <div className="text-sm text-purple-700">Recommendations</div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">AI Insights</h4>
                    <div className="text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
                      {analysis.ai_insights}
                    </div>
                  </div>
                </div>

                {/* Recommendations */}
                <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Optimization Recommendations</h3>
                  <div className="space-y-4">
                    {recommendations.map((rec, index) => (
                      <div key={rec.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between mb-2">
                          <h4 className="font-medium text-gray-900">{rec.description}</h4>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            rec.priority === 'High' ? 'bg-red-100 text-red-800' :
                            rec.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {rec.priority} Priority
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{rec.impact}</p>
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-green-600 font-medium">
                            Estimated Savings: ${rec.savings_estimate.toFixed(2)}/month
                          </span>
                          <span className="text-gray-500">
                            Complexity: {rec.implementation_complexity}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Alerts Tab */}
        {activeTab === 'alerts' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Cost Anomaly Alerts</h2>
              <span className="text-sm text-gray-600">
                {alerts.filter(alert => !alert.resolved).length} active alerts
              </span>
            </div>
            
            <div className="space-y-4">
              {alerts.length === 0 ? (
                <div className="text-center py-12 bg-white rounded-xl shadow-sm border border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Alerts</h3>
                  <p className="text-gray-600">All your clusters are running smoothly!</p>
                </div>
              ) : (
                alerts.map((alert) => (
                  <div key={alert.id} className={`bg-white rounded-xl shadow-sm p-6 border ${
                    alert.resolved ? 'border-gray-200 opacity-60' : 
                    alert.severity === 'high' ? 'border-red-200' :
                    alert.severity === 'medium' ? 'border-yellow-200' :
                    'border-blue-200'
                  }`}>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            alert.severity === 'high' ? 'bg-red-100 text-red-800' :
                            alert.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {alert.severity.toUpperCase()}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(alert.detected_at).toLocaleString()}
                          </span>
                          {alert.resolved && (
                            <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800">
                              RESOLVED
                            </span>
                          )}
                        </div>
                        <h3 className="font-medium text-gray-900 mb-1">
                          {alert.alert_type.replace('_', ' ').toUpperCase()}
                        </h3>
                        <p className="text-gray-600 text-sm">{alert.description}</p>
                      </div>
                      {!alert.resolved && (
                        <button
                          onClick={() => resolveAlert(alert.id)}
                          className="ml-4 px-3 py-1 text-sm bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                        >
                          Resolve
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;