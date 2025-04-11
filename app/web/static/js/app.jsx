import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { Line, Bar } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend
} from 'chart.js';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    BarElement,
    Title,
    Tooltip,
    Legend
);

const Dashboard = () => {
    const [insights, setInsights] = useState(null);
    const [isMonitoring, setIsMonitoring] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchInsights, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchStatus = async () => {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            setIsMonitoring(data.data.is_running);
        } catch (err) {
            setError('Failed to fetch status');
        }
    };

    const fetchInsights = async () => {
        try {
            const response = await fetch('/api/metrics');
            const data = await response.json();
            setInsights(data.data);
        } catch (err) {
            setError('Failed to fetch insights');
        }
    };

    const toggleMonitoring = async () => {
        try {
            const endpoint = isMonitoring ? '/api/stop' : '/api/start';
            const response = await fetch(endpoint, { method: 'POST' });
            const data = await response.json();
            if (data.status === 'success') {
                setIsMonitoring(!isMonitoring);
            }
        } catch (err) {
            setError('Failed to toggle monitoring');
        }
    };

    const activityChartData = {
        labels: insights?.activity_data?.map(d => new Date(d.timestamp).toLocaleTimeString()) || [],
        datasets: [
            {
                label: 'Activity Level',
                data: insights?.activity_data?.map(d => d.activity_level) || [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }
        ]
    };

    const postureChartData = {
        labels: insights?.webcam_data?.map(d => new Date(d.timestamp).toLocaleTimeString()) || [],
        datasets: [
            {
                label: 'Posture Quality',
                data: insights?.webcam_data?.map(d => d.posture_quality) || [],
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }
        ]
    };

    const stressChartData = {
        labels: ['Current Stress Level'],
        datasets: [
            {
                label: 'Stress Score',
                data: [insights?.stress_levels?.stress_score || 0],
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
            }
        ]
    };

    const ergonomicRiskData = {
        labels: ['Posture Risk', 'Activity Risk', 'Break Compliance'],
        datasets: [
            {
                label: 'Risk Factors',
                data: [
                    insights?.ergonomic_risk?.posture_risk || 0,
                    insights?.ergonomic_risk?.activity_risk || 0,
                    insights?.ergonomic_risk?.break_compliance || 0
                ],
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)'
                ],
            }
        ]
    };

    const healthRiskData = {
        labels: ['Health Risk Level'],
        datasets: [
            {
                label: 'Risk Score',
                data: [insights?.health_risk?.risk_level || 0],
                backgroundColor: [
                    insights?.health_risk?.risk_level > 0.7 ? 'rgba(255, 99, 132, 0.5)' :
                    insights?.health_risk?.risk_level > 0.4 ? 'rgba(255, 206, 86, 0.5)' :
                    'rgba(75, 192, 192, 0.5)'
                ],
            }
        ]
    };

    const focusAnalysisData = {
        labels: insights?.focus_analysis?.focus_periods?.map((_, i) => `Period ${i + 1}`) || [],
        datasets: [
            {
                label: 'Focus Score',
                data: insights?.focus_analysis?.focus_periods?.map(p => p.focus_score) || [],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
            }
        ]
    };

    const breakOpportunitiesData = {
        labels: insights?.break_opportunities?.map((_, i) => `Opportunity ${i + 1}`) || [],
        datasets: [
            {
                label: 'Quality Score',
                data: insights?.break_opportunities?.map(o => o.quality_score) || [],
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
            }
        ]
    };

    return (
        <div className="dashboard">
            <h1>HR Analytics Dashboard</h1>
            
            {error && <div className="error">{error}</div>}
            
            <button onClick={toggleMonitoring}>
                {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
            </button>
            
            <div className="metrics-grid">
                <div className="metric-card">
                    <h2>Activity Level</h2>
                    <Line data={activityChartData} />
                </div>
                
                <div className="metric-card">
                    <h2>Posture Quality</h2>
                    <Line data={postureChartData} />
                </div>
                
                <div className="metric-card">
                    <h2>Stress Levels</h2>
                    <Bar data={stressChartData} />
                    <p>Current Level: {insights?.stress_levels?.stress_level || 'Unknown'}</p>
                </div>
                
                <div className="metric-card">
                    <h2>Ergonomic Risk Factors</h2>
                    <Bar data={ergonomicRiskData} />
                    <p>Overall Risk Score: {(insights?.ergonomic_risk?.overall_risk_score * 100).toFixed(1)}%</p>
                </div>
                
                <div className="metric-card">
                    <h2>Health Risk Assessment</h2>
                    <div className="risk-indicator">
                        <div className="risk-level" style={{
                            width: `${(insights?.health_risk?.risk_level || 0) * 100}%`,
                            backgroundColor: insights?.health_risk?.risk_level > 0.7 ? '#ff6384' :
                                          insights?.health_risk?.risk_level > 0.4 ? '#ffce56' :
                                          '#36a2eb'
                        }}></div>
                    </div>
                    <p>Confidence: {(insights?.health_risk?.confidence || 0) * 100}%</p>
                </div>
                
                <div className="metric-card">
                    <h2>Focus Time Analysis</h2>
                    <div className="focus-stats">
                        <p>Total Time: {Math.round(insights?.focus_analysis?.total_time_minutes || 0)} minutes</p>
                        <p>Focus Time: {Math.round(insights?.focus_analysis?.focus_time_minutes || 0)} minutes</p>
                        <p>Focus Percentage: {Math.round(insights?.focus_analysis?.focus_percentage || 0)}%</p>
                    </div>
                    <div className="chart-container">
                        <Bar data={focusAnalysisData} options={{
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    max: 1
                                }
                            }
                        }} />
                    </div>
                </div>
                
                <div className="metric-card">
                    <h2>Break Opportunities</h2>
                    <div className="break-opportunities">
                        {insights?.break_opportunities?.map((opp, index) => (
                            <div key={index} className="break-opportunity">
                                <p>Time: {new Date(opp.start_time).toLocaleTimeString()} - 
                                   {new Date(opp.end_time).toLocaleTimeString()}</p>
                                <p>Duration: {opp.duration_minutes} minutes</p>
                                <p>Quality Score: {Math.round(opp.quality_score * 100)}%</p>
                                <p>Confidence: {Math.round(opp.confidence * 100)}%</p>
                            </div>
                        ))}
                    </div>
                    <div className="chart-container">
                        <Bar data={breakOpportunitiesData} options={{
                            responsive: true,
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    max: 1
                                }
                            }
                        }} />
                    </div>
                </div>
            </div>
        </div>
    );
};

ReactDOM.render(<Dashboard />, document.getElementById('root')); 