import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { ChartBarIcon, ClockIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

interface BenchmarkMetrics {
  total_runs: number;
  success_rate: number;
  average_processing_time: number;
  average_quality_score: number;
  average_response_time: number;
  trend_data: Array<{
    date: string;
    quality_score: number;
    processing_time: number;
  }>;
}

interface BenchmarkDashboardProps {
  metrics: BenchmarkMetrics;
}

export default function BenchmarkDashboard({ metrics }: BenchmarkDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Benchmark Dashboard</h2>
        <p className="text-gray-600">System performance metrics and trends</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-blue-500" />
            <div className="ml-3">
              <p className="text-2xl font-semibold text-gray-900">
                {metrics.total_runs}
              </p>
              <p className="text-sm text-gray-500">Total Runs</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <CheckCircleIcon className="h-8 w-8 text-green-500" />
            <div className="ml-3">
              <p className="text-2xl font-semibold text-gray-900">
                {(metrics.success_rate * 100).toFixed(1)}%
              </p>
              <p className="text-sm text-gray-500">Success Rate</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <ClockIcon className="h-8 w-8 text-yellow-500" />
            <div className="ml-3">
              <p className="text-2xl font-semibold text-gray-900">
                {metrics.average_processing_time.toFixed(1)}s
              </p>
              <p className="text-sm text-gray-500">Avg Processing Time</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-purple-500" />
            <div className="ml-3">
              <p className="text-2xl font-semibold text-gray-900">
                {metrics.average_quality_score.toFixed(2)}
              </p>
              <p className="text-sm text-gray-500">Quality Score</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quality Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quality Score Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={metrics.trend_data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 1]} />
              <Tooltip />
              <Line type="monotone" dataKey="quality_score" stroke="#3b82f6" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Processing Time Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Processing Time Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={metrics.trend_data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="processing_time" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}