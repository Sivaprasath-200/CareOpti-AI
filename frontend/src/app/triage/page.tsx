'use client';
import { useState } from 'react';

export default function TriagePage() {
  const [formData, setFormData] = useState({
    age: 45,
    heart_rate: 75,
    systolic_bp: 120,
    diastolic_bp: 80,
    respiratory_rate: 16,
    oxygen_saturation: 98,
    temperature: 37.0,
    chest_pain: 0,
    shortness_of_breath: 0,
    fever: 0,
    severe_bleeding: 0,
    altered_consciousness: 0
  });
  
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/v1/triage/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error(error);
      alert('Error connecting to Triage API');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.type === 'checkbox' ? (e.target.checked ? 1 : 0) : Number(e.target.value);
    setFormData({ ...formData, [e.target.name]: value });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6 border-b pb-4">AI-Assisted Patient Triage</h1>
        
        {/* WARNING BANNER */}
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                CLINICAL WARNING: AI-Assisted Recommendation Only
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>This system provides AI-assisted triage severity predictions based on synthetic models. It does <strong>NOT</strong> establish clinical validity and must <strong>NOT</strong> be used to autonomously diagnose or admit patients. All recommendations require qualified clinical review.</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">Clinical Inputs</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Age</label>
                <input type="number" name="age" value={formData.age} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black border p-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Heart Rate (BPM)</label>
                <input type="number" name="heart_rate" value={formData.heart_rate} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black border p-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Systolic BP</label>
                <input type="number" name="systolic_bp" value={formData.systolic_bp} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black border p-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Diastolic BP</label>
                <input type="number" name="diastolic_bp" value={formData.diastolic_bp} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black border p-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Resp Rate</label>
                <input type="number" name="respiratory_rate" value={formData.respiratory_rate} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black border p-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">SpO2 (%)</label>
                <input type="number" name="oxygen_saturation" value={formData.oxygen_saturation} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black border p-2" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Temp (°C)</label>
                <input type="number" name="temperature" step="0.1" value={formData.temperature} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black border p-2" />
              </div>
            </div>

            <h3 className="text-lg font-semibold mt-6 mb-2 text-gray-700">Symptoms & Risk Factors</h3>
            <div className="grid grid-cols-2 gap-2 text-black">
              <label className="flex items-center space-x-2">
                <input type="checkbox" name="chest_pain" checked={formData.chest_pain === 1} onChange={handleChange} className="rounded text-blue-600" />
                <span className="text-sm">Chest Pain</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="checkbox" name="shortness_of_breath" checked={formData.shortness_of_breath === 1} onChange={handleChange} className="rounded text-blue-600" />
                <span className="text-sm">Shortness of Breath</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="checkbox" name="fever" checked={formData.fever === 1} onChange={handleChange} className="rounded text-blue-600" />
                <span className="text-sm">Fever</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="checkbox" name="severe_bleeding" checked={formData.severe_bleeding === 1} onChange={handleChange} className="rounded text-blue-600" />
                <span className="text-sm">Severe Bleeding</span>
              </label>
              <label className="flex items-center space-x-2">
                <input type="checkbox" name="altered_consciousness" checked={formData.altered_consciousness === 1} onChange={handleChange} className="rounded text-blue-600" />
                <span className="text-sm">Altered Consciousness</span>
              </label>
            </div>

            <button type="submit" disabled={loading} className="w-full mt-6 bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 transition disabled:bg-blue-300">
              {loading ? 'Analyzing...' : 'Generate AI Triage Prediction'}
            </button>
          </form>

          <div className="bg-gray-100 rounded-lg p-6 border border-gray-200">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">Prediction Results</h2>
            {result ? (
              <div className="space-y-4">
                <div className={`p-4 rounded-lg font-bold text-lg text-center text-white ${
                  result.severity === 'EMERGENCY' ? 'bg-red-600' :
                  result.severity === 'CRITICAL' ? 'bg-orange-500' :
                  result.severity === 'HIGH' ? 'bg-yellow-500' :
                  result.severity === 'MODERATE' ? 'bg-blue-500' : 'bg-green-500'
                }`}>
                  Predicted Triage Category: {result.severity}
                </div>
                
                <div className="bg-white p-4 rounded border text-black">
                  <p className="font-semibold text-gray-700">Model Confidence: <span className="font-normal text-blue-600">{(result.confidence * 100).toFixed(1)}%</span></p>
                  <p className="text-xs text-gray-500 mt-1">Version: {result.model_version}</p>
                </div>

                <div className="bg-white p-4 rounded border">
                  <h4 className="font-semibold text-gray-700 mb-2">Top Contributing Factors (SHAP Explainability)</h4>
                  <ul className="space-y-2">
                    {result.contributing_factors.map((f: any, i: number) => (
                      <li key={i} className="flex justify-between items-center text-sm">
                        <span className="font-medium text-gray-600">{f.feature.replace(/_/g, ' ')}</span>
                        <span className="text-gray-500 text-xs">Value: {f.value}</span>
                        <span className={`px-2 py-1 rounded text-xs ${f.impact > 0 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                          Impact: {f.impact > 0 ? '+' : ''}{f.impact.toFixed(3)}
                        </span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400">
                <p>Awaiting inputs...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
