'use client';
import { useState } from 'react';

export default function CDSSPage() {
  const [patientId, setPatientId] = useState('');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleEvaluate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/cdss/evaluate?patient_id=${patientId}`, {
        method: 'POST'
      });
      const data = await res.json();
      if (!res.ok) {
        setMessage(`Error: ${data.detail || 'Failed to run CDSS'}`);
        setResult(null);
      } else {
        setResult(data);
      }
    } catch (error) {
      console.error(error);
      setMessage('Network error connecting to CDSS API');
    } finally {
      setLoading(false);
    }
  };

  const handleAcknowledge = async (alertId: string) => {
    setLoading(true);
    try {
      // Dummy reviewer ID for demo
      const reviewer_id = '00000000-0000-0000-0000-000000000000';
      const res = await fetch(`http://127.0.0.1:8000/api/v1/cdss/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer_id, review_note: "Acknowledged by Clinician" })
      });
      if (res.ok) {
        // Optimistically update the UI
        setResult((prev: any) => ({
          ...prev,
          clinical_alerts: prev.clinical_alerts.map((a: any) => 
            a.id === alertId ? { ...a, is_acknowledged: true } : a
          )
        }));
      } else {
        setMessage('Failed to acknowledge alert');
      }
    } catch (error) {
      setMessage('Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        
        {/* Header & Warning */}
        <div className="bg-white rounded-xl shadow-sm p-6 border-l-4 border-yellow-500">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Clinical Decision Support System (CDSS)</h1>
          <p className="text-yellow-700 font-semibold flex items-center">
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
            Clinical decision support only — requires qualified clinician review. This system does NOT make final treatment or diagnostic decisions.
          </p>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-xl shadow-sm p-6 text-black">
          <form onSubmit={handleEvaluate} className="flex gap-4 items-end">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Patient UUID</label>
              <input 
                type="text" 
                value={patientId} 
                onChange={e => setPatientId(e.target.value)} 
                required
                placeholder="e.g. 123e4567-..."
                className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2 text-black" 
              />
            </div>
            <button 
              type="submit" 
              disabled={loading || !patientId} 
              className="bg-indigo-600 text-white px-6 py-2 rounded-md font-semibold hover:bg-indigo-700 transition disabled:bg-indigo-300"
            >
              {loading ? 'Evaluating...' : 'Run CDSS Evaluation'}
            </button>
          </form>
          {message && <p className="mt-4 text-sm font-medium text-red-600">{message}</p>}
        </div>

        {/* Results */}
        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 text-black">
            
            {/* Risk Assessment */}
            <div className="lg:col-span-1 space-y-6">
              <div className="bg-white rounded-xl shadow-sm p-6 border-t-4 border-indigo-500">
                <h2 className="text-lg font-bold text-gray-800 mb-4">Deterioration Risk</h2>
                {result.risk_assessment ? (
                  <>
                    <div className="text-center mb-6">
                      <p className={`text-4xl font-extrabold ${result.risk_assessment.risk_category === 'CRITICAL' || result.risk_assessment.risk_category === 'HIGH' ? 'text-red-600' : 'text-green-600'}`}>
                        {result.risk_assessment.risk_category}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">Score: {result.risk_assessment.risk_score.toFixed(1)} / 100</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded text-sm">
                      <p><strong>Model:</strong> {result.risk_assessment.model_name} (v{result.risk_assessment.model_version})</p>
                      <p className="mt-2 text-xs text-gray-500">Technical prototype trained on synthetic data. NOT clinically validated.</p>
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-gray-500">No risk assessment available.</p>
                )}
              </div>

              {/* Guidelines */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-lg font-bold text-gray-800 mb-4">Relevant Guidelines</h2>
                {result.guideline_matches?.length > 0 ? (
                  <div className="space-y-4">
                    {result.guideline_matches.map((g: any, i: number) => (
                      <div key={i} className="border-l-2 border-blue-400 pl-3">
                        <p className="font-semibold text-sm text-blue-900">{g.title}</p>
                        <p className="text-xs text-gray-600 mt-1">{g.recommendation_mappings?.action}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No matching guidelines triggered.</p>
                )}
              </div>
            </div>

            {/* Alerts */}
            <div className="lg:col-span-2 space-y-6">
              
              {/* Clinical Alerts */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-lg font-bold text-gray-800 mb-4">Clinical Rule Alerts</h2>
                {result.clinical_alerts?.length > 0 ? (
                  <div className="space-y-4">
                    {result.clinical_alerts.map((a: any) => (
                      <div key={a.id} className={`p-4 rounded-lg border ${a.severity === 'CRITICAL' ? 'bg-red-50 border-red-200' : a.severity === 'HIGH' ? 'bg-orange-50 border-orange-200' : 'bg-yellow-50 border-yellow-200'}`}>
                        <div className="flex justify-between items-start">
                          <div>
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-white text-gray-800 shadow-sm mb-2 border">
                              {a.severity} • {a.category}
                            </span>
                            <p className="font-bold text-gray-900">{a.message}</p>
                            <p className="text-sm text-gray-700 mt-1"><strong>Trigger Value:</strong> {a.supporting_value}</p>
                          </div>
                          {!a.is_acknowledged ? (
                            <button onClick={() => handleAcknowledge(a.id)} className="bg-blue-600 text-white text-xs px-3 py-1.5 rounded hover:bg-blue-700">
                              Acknowledge
                            </button>
                          ) : (
                            <span className="text-green-600 text-xs font-bold flex items-center">
                              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd"></path></svg>
                              Reviewed
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No clinical rule violations detected.</p>
                )}
              </div>

              {/* Medication Alerts */}
              <div className="bg-white rounded-xl shadow-sm p-6">
                <h2 className="text-lg font-bold text-gray-800 mb-4">Medication Safety Warnings</h2>
                {result.medication_alerts?.length > 0 ? (
                  <div className="space-y-4">
                    {result.medication_alerts.map((m: any) => (
                      <div key={m.id} className="p-4 rounded-lg bg-pink-50 border border-pink-200 flex justify-between items-center">
                        <div>
                           <p className="font-bold text-pink-900">{m.alert_type}: {m.medication}</p>
                           <p className="text-sm text-pink-800 mt-1">{m.explanation}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">No medication safety conflicts detected.</p>
                )}
              </div>

            </div>
          </div>
        )}

      </div>
    </div>
  );
}
