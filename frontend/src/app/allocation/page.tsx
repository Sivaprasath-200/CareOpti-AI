'use client';
import { useState } from 'react';

export default function ResourceAllocationPage() {
  const [admissionId, setAdmissionId] = useState('');
  const [severity, setSeverity] = useState('EMERGENCY');
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleOptimize = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');
    try {
      const res = await fetch(`http://127.0.0.1:8000/api/v1/admissions/${admissionId}/optimize?severity=${severity}`, {
        method: 'POST'
      });
      const data = await res.json();
      if (!res.ok) {
        setMessage(`Error: ${data.detail?.message || 'Failed to optimize'}`);
        setResult(null);
      } else {
        setResult(data);
      }
    } catch (error) {
      console.error(error);
      setMessage('Network error connecting to Allocation API');
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (action: 'APPROVE' | 'REJECT') => {
    setLoading(true);
    try {
      // Dummy reviewer ID for demo
      const reviewer_id = '00000000-0000-0000-0000-000000000000';
      const res = await fetch(`http://127.0.0.1:8000/api/v1/admissions/${admissionId}/confirm-allocation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reviewer_id, action })
      });
      const data = await res.json();
      if (res.ok) {
        setMessage(`Success: ${data.message}`);
        setResult((prev: any) => ({ ...prev, status: data.status }));
      } else {
        setMessage(`Error: ${data.detail || 'Failed to submit review'}`);
      }
    } catch (error) {
      setMessage('Network error connecting to Allocation API');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6 border-b pb-4">Smart Resource Allocation Engine</h1>
        
        {/* WARNING BANNER */}
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-8 rounded">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-500" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3 text-sm text-blue-700">
              <p><strong>AI-Assisted Optimization Recommendation:</strong> This system uses ILP optimization to suggest resources. All recommendations require authorized clinical/hospital staff review before final allocation.</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-1 border-r pr-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">Admission Details</h2>
            <form onSubmit={handleOptimize} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Admission UUID</label>
                <input 
                  type="text" 
                  value={admissionId} 
                  onChange={e => setAdmissionId(e.target.value)} 
                  required
                  placeholder="e.g. 123e4567-..."
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black border p-2" 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Triage Severity (from Phase 4)</label>
                <select 
                  value={severity} 
                  onChange={e => setSeverity(e.target.value)}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-black border p-2"
                >
                  <option value="EMERGENCY">EMERGENCY (Requires ICU)</option>
                  <option value="CRITICAL">CRITICAL (Requires ICU)</option>
                  <option value="HIGH">HIGH</option>
                  <option value="MODERATE">MODERATE</option>
                  <option value="LOW">LOW</option>
                </select>
              </div>
              <button 
                type="submit" 
                disabled={loading || !admissionId} 
                className="w-full bg-indigo-600 text-white py-2 rounded-lg font-semibold hover:bg-indigo-700 transition disabled:bg-indigo-300"
              >
                {loading ? 'Optimizing...' : 'Run Optimization'}
              </button>
            </form>
            {message && <p className="mt-4 text-sm font-medium text-red-600">{message}</p>}
          </div>

          <div className="md:col-span-2">
            <h2 className="text-xl font-semibold mb-4 text-gray-700">Optimization Result</h2>
            {result ? (
              <div className="space-y-4 text-black">
                <div className="flex justify-between items-center bg-gray-100 p-4 rounded-lg">
                  <div>
                    <p className="text-xs text-gray-500 uppercase">Status</p>
                    <p className={`font-bold ${result.status === 'RECOMMENDED' ? 'text-yellow-600' : result.status === 'APPROVED' ? 'text-green-600' : 'text-red-600'}`}>
                      {result.status}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase">Score</p>
                    <p className="font-bold text-gray-800">{result.optimization_score}</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="border p-4 rounded bg-white shadow-sm">
                    <p className="text-sm text-gray-500">Recommended Bed</p>
                    <p className="font-medium text-indigo-700 font-mono text-sm break-all">{result.recommended_bed_id}</p>
                  </div>
                  <div className="border p-4 rounded bg-white shadow-sm">
                    <p className="text-sm text-gray-500">Recommended Doctor</p>
                    <p className="font-medium text-indigo-700 font-mono text-sm break-all">{result.recommended_doctor_id}</p>
                  </div>
                </div>

                <div className="bg-white p-4 rounded border text-sm text-gray-700">
                  <h4 className="font-semibold mb-2">Constraint Evidence</h4>
                  <p><strong>Hard Constraints Passed:</strong> {result.constraints_evidence.hard_constraints_passed ? 'Yes' : 'No'}</p>
                  <ul className="list-disc pl-5 mt-2 text-xs">
                    {result.constraints_evidence.reasons.map((r: string, i: number) => <li key={i}>{r}</li>)}
                  </ul>
                </div>

                {result.status === 'RECOMMENDED' && (
                  <div className="flex space-x-4 pt-4 border-t">
                    <button 
                      onClick={() => handleReview('APPROVE')} 
                      className="flex-1 bg-green-600 text-white py-3 rounded font-semibold hover:bg-green-700 transition"
                    >
                      Approve Allocation
                    </button>
                    <button 
                      onClick={() => handleReview('REJECT')} 
                      className="flex-1 bg-red-600 text-white py-3 rounded font-semibold hover:bg-red-700 transition"
                    >
                      Reject Allocation
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-gray-400 border-2 border-dashed rounded-lg">
                <p>No recommendation active.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
