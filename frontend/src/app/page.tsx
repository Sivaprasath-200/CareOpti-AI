import Link from 'next/link';
import React from 'react';

export default function Dashboard() {
  return (
    <div className="flex h-screen bg-gray-50 text-gray-900 font-sans overflow-hidden">
      {/* SIDEBAR NAVIGATION */}
      <aside className="w-64 bg-white border-r border-gray-200 hidden md:flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-xl font-bold text-blue-700 leading-tight">Holistic Healthcare Intelligence</h2>
        </div>
        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <Link href="/" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md bg-blue-50 text-blue-700">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>
            Dashboard
          </Link>
          <div className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900 cursor-not-allowed opacity-75">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>
            Patients / EHR <span className="text-xs text-gray-400 ml-auto">(TBD)</span>
          </div>
          <div className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900 cursor-not-allowed opacity-75">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
            Policy Engine <span className="text-xs text-gray-400 ml-auto">(API)</span>
          </div>
          <Link href="/triage" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
            AI Triage
          </Link>
          <Link href="/allocation" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
            Resource Allocation
          </Link>
          <Link href="/cdss" className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
            Clinical Decision Support
          </Link>
          <div className="flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-gray-600 hover:bg-gray-50 hover:text-gray-900 cursor-not-allowed opacity-75">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
            System / Audit <span className="text-xs text-gray-400 ml-auto">(TBD)</span>
          </div>
        </nav>
      </aside>

      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* HEADER */}
        <header className="bg-white border-b border-gray-200 shadow-sm z-10">
          <div className="flex items-center justify-between px-6 py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-800 hidden md:block">Holistic Healthcare Intelligence</h1>
              <p className="text-sm text-gray-500 font-medium">Policy-Integrated Admission & Treatment Intelligence</p>
            </div>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                </span>
                <span className="text-sm font-medium text-gray-600">System Online</span>
              </div>
              <div className="hidden md:flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold border border-blue-200">
                  DR
                </div>
                <div className="text-sm font-medium">
                  <div>Dr. Smith</div>
                  <div className="text-xs text-gray-500">Attending Physician</div>
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          
          {/* SAFETY DISCLAIMER */}
          <div className="mb-8 bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-md shadow-sm">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-amber-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-amber-800">Important Safety Notice</h3>
                <div className="mt-2 text-sm text-amber-700">
                  <p>
                    Clinical decision-support prototype using synthetic data. AI outputs are recommendations only and require qualified clinical review. 
                    The system is not clinically validated and does not replace professional medical judgment.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* DASHBOARD OVERVIEW */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
              <p className="text-sm font-medium text-gray-500">Active Admissions</p>
              <div className="mt-2 flex items-baseline gap-2">
                <p className="text-3xl font-bold text-gray-900">--</p>
                <p className="text-sm font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">Demo</p>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
              <p className="text-sm font-medium text-gray-500">Available Beds</p>
              <div className="mt-2 flex items-baseline gap-2">
                <p className="text-3xl font-bold text-gray-900">--</p>
                <p className="text-sm font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">Demo</p>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
              <p className="text-sm font-medium text-gray-500">AI Triage Cases</p>
              <div className="mt-2 flex items-baseline gap-2">
                <p className="text-3xl font-bold text-gray-900">--</p>
                <p className="text-sm font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">Demo</p>
              </div>
            </div>
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-5">
              <p className="text-sm font-medium text-gray-500">Critical Alerts</p>
              <div className="mt-2 flex items-baseline gap-2">
                <p className="text-3xl font-bold text-gray-900">--</p>
                <p className="text-sm font-medium text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">Demo</p>
              </div>
            </div>
          </div>

          {/* SYSTEM WORKFLOW */}
          <div className="mb-8">
            <h2 className="text-lg font-bold text-gray-800 mb-4">AI-Assisted Decision-Support Workflow</h2>
            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-6 overflow-x-auto">
              <div className="flex items-center min-w-max text-sm font-medium text-center">
                <div className="bg-gray-50 border border-gray-200 text-gray-700 py-3 px-4 rounded shadow-sm w-40">Patient / EHR</div>
                <div className="w-8 h-px bg-gray-300 mx-2 relative">
                  <div className="absolute right-0 -top-1.5 border-t-[6px] border-t-transparent border-l-[6px] border-l-gray-400 border-b-[6px] border-b-transparent"></div>
                </div>
                <div className="bg-indigo-50 border border-indigo-200 text-indigo-700 py-3 px-4 rounded shadow-sm w-40">Policy Evaluation</div>
                <div className="w-8 h-px bg-gray-300 mx-2 relative">
                  <div className="absolute right-0 -top-1.5 border-t-[6px] border-t-transparent border-l-[6px] border-l-gray-400 border-b-[6px] border-b-transparent"></div>
                </div>
                <div className="bg-blue-50 border border-blue-200 text-blue-700 py-3 px-4 rounded shadow-sm w-40">AI Triage</div>
                <div className="w-8 h-px bg-gray-300 mx-2 relative">
                  <div className="absolute right-0 -top-1.5 border-t-[6px] border-t-transparent border-l-[6px] border-l-gray-400 border-b-[6px] border-b-transparent"></div>
                </div>
                <div className="bg-purple-50 border border-purple-200 text-purple-700 py-3 px-4 rounded shadow-sm w-40">Resource Optimization</div>
                <div className="w-8 h-px bg-gray-300 mx-2 relative">
                  <div className="absolute right-0 -top-1.5 border-t-[6px] border-t-transparent border-l-[6px] border-l-gray-400 border-b-[6px] border-b-transparent"></div>
                </div>
                <div className="bg-rose-50 border border-rose-200 text-rose-700 py-3 px-4 rounded shadow-sm w-44">Clinical Decision Support</div>
                <div className="w-8 h-px bg-gray-300 mx-2 relative">
                  <div className="absolute right-0 -top-1.5 border-t-[6px] border-t-transparent border-l-[6px] border-l-gray-400 border-b-[6px] border-b-transparent"></div>
                </div>
                <div className="bg-emerald-50 border border-emerald-200 text-emerald-800 py-3 px-4 rounded shadow-sm w-40">Clinician Review</div>
              </div>
              <p className="text-xs text-gray-500 mt-4 italic text-center md:text-left">Final clinical decisions remain with qualified healthcare professionals.</p>
            </div>
          </div>

          <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
            <div className="xl:col-span-2 space-y-6">
              <h2 className="text-lg font-bold text-gray-800">Core Modules</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                
                {/* POLICY ENGINE */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 transition-colors flex flex-col h-full">
                  <div className="p-5 flex-1">
                    <div className="w-10 h-10 rounded bg-indigo-100 flex items-center justify-center text-indigo-600 mb-4">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Policy-Integrated Engine</h3>
                    <p className="text-gray-600 text-sm mb-4">Automated policy eligibility, authorization and hospital protocol evaluation.</p>
                    <div className="flex flex-wrap gap-2">
                      <span className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded font-medium">Deterministic Rules</span>
                    </div>
                  </div>
                  <div className="border-t border-gray-100 p-4 bg-gray-50 rounded-b-lg">
                    <button disabled className="w-full text-center text-sm font-medium text-indigo-600 bg-indigo-50 border border-indigo-200 rounded py-2 opacity-50 cursor-not-allowed">API Only / Coming Soon</button>
                  </div>
                </div>

                {/* AI TRIAGE */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 transition-colors flex flex-col h-full">
                  <div className="p-5 flex-1">
                    <div className="w-10 h-10 rounded bg-blue-100 flex items-center justify-center text-blue-600 mb-4">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">AI Admission Intelligence</h3>
                    <p className="text-gray-600 text-sm mb-4">AI-assisted severity and triage prediction using synthetic-data-trained models.</p>
                    <div className="flex flex-wrap gap-2">
                      <span className="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded font-medium border border-blue-100">XGBoost</span>
                      <span className="bg-blue-50 text-blue-700 text-xs px-2 py-1 rounded font-medium border border-blue-100">SHAP Explainability</span>
                    </div>
                  </div>
                  <div className="border-t border-gray-100 p-4 bg-gray-50 rounded-b-lg">
                    <Link href="/triage" className="block w-full text-center text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded py-2 transition-colors">Open AI Triage</Link>
                  </div>
                </div>

                {/* RESOURCE ALLOCATION */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 transition-colors flex flex-col h-full">
                  <div className="p-5 flex-1">
                    <div className="w-10 h-10 rounded bg-purple-100 flex items-center justify-center text-purple-600 mb-4">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" /></svg>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Smart Resource Allocation</h3>
                    <p className="text-gray-600 text-sm mb-4">Optimization-assisted bed, ward and doctor allocation.</p>
                    <div className="flex flex-wrap gap-2">
                      <span className="bg-purple-50 text-purple-700 text-xs px-2 py-1 rounded font-medium border border-purple-100">PuLP ILP Optimization</span>
                    </div>
                  </div>
                  <div className="border-t border-gray-100 p-4 bg-gray-50 rounded-b-lg">
                    <Link href="/allocation" className="block w-full text-center text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 rounded py-2 transition-colors">Open Resource Allocation</Link>
                  </div>
                </div>

                {/* CDSS */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 hover:border-blue-300 transition-colors flex flex-col h-full">
                  <div className="p-5 flex-1">
                    <div className="w-10 h-10 rounded bg-rose-100 flex items-center justify-center text-rose-600 mb-4">
                      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Clinical Decision Support</h3>
                    <p className="text-gray-600 text-sm mb-4">Clinical rules, deterioration risk, medication safety and alerts.</p>
                    <div className="flex flex-wrap gap-2">
                      <span className="bg-rose-50 text-rose-700 text-xs px-2 py-1 rounded font-medium border border-rose-100">XGBoost Risk Model</span>
                      <span className="bg-rose-50 text-rose-700 text-xs px-2 py-1 rounded font-medium border border-rose-100">Clinical Rules</span>
                      <span className="bg-rose-50 text-rose-700 text-xs px-2 py-1 rounded font-medium border border-rose-100">Medication Safety</span>
                    </div>
                  </div>
                  <div className="border-t border-gray-100 p-4 bg-gray-50 rounded-b-lg">
                    <Link href="/cdss" className="block w-full text-center text-sm font-medium text-white bg-rose-600 hover:bg-rose-700 rounded py-2 transition-colors">Open CDSS</Link>
                  </div>
                </div>

              </div>
            </div>

            <div className="xl:col-span-1 space-y-6">
              <h2 className="text-lg font-bold text-gray-800">Recent Activity</h2>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div className="p-4 border-b border-gray-100 bg-gray-50">
                  <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">System Logs (Synthetic)</span>
                </div>
                <ul className="divide-y divide-gray-100">
                  <li className="p-4 flex gap-4 hover:bg-gray-50">
                    <div className="mt-1 flex-shrink-0 w-2 h-2 rounded-full bg-blue-500"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Clinical alert acknowledged</p>
                      <p className="text-xs text-gray-500 mt-1">Dr. Smith reviewed patient vitals.</p>
                      <p className="text-xs text-gray-400 mt-1">10 mins ago</p>
                    </div>
                  </li>
                  <li className="p-4 flex gap-4 hover:bg-gray-50">
                    <div className="mt-1 flex-shrink-0 w-2 h-2 rounded-full bg-rose-500"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">CDSS alert generated</p>
                      <p className="text-xs text-gray-500 mt-1">High deterioration risk detected for patient.</p>
                      <p className="text-xs text-gray-400 mt-1">12 mins ago</p>
                    </div>
                  </li>
                  <li className="p-4 flex gap-4 hover:bg-gray-50">
                    <div className="mt-1 flex-shrink-0 w-2 h-2 rounded-full bg-purple-500"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Resource allocation recommendation created</p>
                      <p className="text-xs text-gray-500 mt-1">ICU Bed recommended.</p>
                      <p className="text-xs text-gray-400 mt-1">15 mins ago</p>
                    </div>
                  </li>
                  <li className="p-4 flex gap-4 hover:bg-gray-50">
                    <div className="mt-1 flex-shrink-0 w-2 h-2 rounded-full bg-blue-500"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">AI triage assessment generated</p>
                      <p className="text-xs text-gray-500 mt-1">Severity: CRITICAL.</p>
                      <p className="text-xs text-gray-400 mt-1">16 mins ago</p>
                    </div>
                  </li>
                  <li className="p-4 flex gap-4 hover:bg-gray-50">
                    <div className="mt-1 flex-shrink-0 w-2 h-2 rounded-full bg-indigo-500"></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Policy evaluation completed</p>
                      <p className="text-xs text-gray-500 mt-1">Status: NOT_ELIGIBLE.</p>
                      <p className="text-xs text-gray-400 mt-1">18 mins ago</p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>

        </main>
        
        {/* FOOTER */}
        <footer className="bg-white border-t border-gray-200 py-4 px-6 text-center text-sm text-gray-500 z-10">
          <p className="font-medium">Holistic Healthcare Intelligence - Phase 1–6 Integrated Prototype</p>
          <p className="mt-1 text-xs">Synthetic Data &bull; AI-Assisted &bull; Human-in-the-Loop</p>
        </footer>
      </div>
    </div>
  );
}
