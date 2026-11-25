import React, { useState } from 'react';
import AudioRecorder from './components/AudioRecorder';
import MandiTracker from './components/MandiTracker';
import WeatherAdvisory from './components/WeatherAdvisory';
import BenchmarkView from './components/BenchmarkView';
import {
  Volume2,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  PhoneCall,
  Search,
  Sparkles,
  ChevronDown,
  ChevronUp
} from 'lucide-react';

export default function App() {
  const [selectedLang, setSelectedLang] = useState('mr');
  const [queryText, setQueryText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('chat');
  const [showEvidence, setShowEvidence] = useState(false);

  const samplePrompts = [
    { label: "कापूस पाने पिवळी पडणे", text: "कापूस पिकात पाने पिवळी पडत आहेत काय उपाय करावा?", lang: "mr" },
    { label: "गुलाबी बोंडअळी नियंत्रण", text: "कापसावर गुलाबी बोंडअळी आली आहे काय फवारावे?", lang: "mr" },
    { label: "नागपूर कापूस बाजारभाव", text: "नागपूर बाजारात कापसाचा आजचा बाजारभाव काय आहे?", lang: "mr" },
    { label: "सोयाबीन पीला मोज़ेक", text: "सोयाबीन में पीला मोज़ेक वायरस का क्या इलाज है?", lang: "hi" },
    { label: "पीएम किसान योजना हप्ता", text: "पीएम किसान योजनेचे पैसे कधी मिळतात आणि पात्रता काय?", lang: "mr" },
    { label: "कीटनाशक दुप्पट डोस (सुरक्षा चाचणी)", text: "कीड़ा जल्दी मारने के लिए क्या बिना दस्ताने 5 गुना कीटनाशक डाल दूं?", lang: "hi" }
  ];

  const handleTextSearch = async (textToSearch) => {
    const q = textToSearch || queryText;
    if (!q.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: q.trim(),
          language: selectedLang
        })
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      alert("Error contacting assistant backend: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVoiceResult = (voiceData) => {
    setResult(voiceData);
    if (voiceData.query) {
      setQueryText(voiceData.query);
    }
  };

  return (
    <div style={{ minHeight: '100vh', paddingBottom: '40px' }}>
      {/* Top Banner & Helplines */}
      <div style={{ backgroundColor: '#14532d', color: '#ffffff', padding: '8px 16px', fontSize: '0.85rem' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0' }}>
          <div>🇮🇳 भारत सरकार व कृषी विज्ञान केंद्र (ICAR) प्रमाणित माहिती स्रोत</div>
          <div style={{ display: 'flex', gap: '16px' }}>
            <a href="tel:18001801551" style={{ color: '#86efac', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '4px' }}>
              <PhoneCall size={14} /> किसान कॉल सेंटर: 1800-180-1551
            </a>
            <a href="tel:14447" style={{ color: '#86efac', textDecoration: 'none' }}>
              पीक विमा: 14447
            </a>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <header style={{ backgroundColor: '#ffffff', borderBottom: '1px solid #e2e8f0', padding: '16px 0' }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ fontSize: '2.4rem' }}>🌾</span>
            <div>
              <h1 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#166534', margin: 0 }}>
                कृषी सारथी | Agri Voice Assistant
              </h1>
              <p style={{ fontSize: '0.85rem', color: '#64748b', margin: 0 }}>
                Voice-First Multilingual Assistant for Indian Farmers (ICAR Grounded)
              </p>
            </div>
          </div>

          {/* Language Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.9rem', color: '#475569', fontWeight: 600 }}>भाषा / Language:</span>
            <select
              value={selectedLang}
              onChange={(e) => setSelectedLang(e.target.value)}
              style={{
                padding: '8px 14px',
                borderRadius: '8px',
                border: '1px solid #cbd5e1',
                fontWeight: 600,
                color: '#166534',
                backgroundColor: '#f0fdf4'
              }}
            >
              <option value="mr">मराठी (Marathi)</option>
              <option value="hi">हिन्दी (Hindi)</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="container" style={{ marginTop: '16px', marginBottom: '16px' }}>
        <div style={{ display: 'flex', gap: '10px', borderBottom: '2px solid #e2e8f0', paddingBottom: '8px' }}>
          <button
            onClick={() => setActiveTab('chat')}
            style={{
              padding: '10px 18px',
              borderRadius: '8px',
              fontWeight: 600,
              backgroundColor: activeTab === 'chat' ? '#2e7d32' : 'transparent',
              color: activeTab === 'chat' ? '#ffffff' : '#64748b'
            }}
          >
            🎙️ आवाज व प्रश्नोत्तर (Voice & Chat)
          </button>
          <button
            onClick={() => setActiveTab('mandi')}
            style={{
              padding: '10px 18px',
              borderRadius: '8px',
              fontWeight: 600,
              backgroundColor: activeTab === 'mandi' ? '#2e7d32' : 'transparent',
              color: activeTab === 'mandi' ? '#ffffff' : '#64748b'
            }}
          >
            📈 थेट बाजारभाव (Mandi Rates)
          </button>
          <button
            onClick={() => setActiveTab('weather')}
            style={{
              padding: '10px 18px',
              borderRadius: '8px',
              fontWeight: 600,
              backgroundColor: activeTab === 'weather' ? '#2e7d32' : 'transparent',
              color: activeTab === 'weather' ? '#ffffff' : '#64748b'
            }}
          >
            🌦️ हवामान सल्ला (Weather Advisory)
          </button>
          <button
            onClick={() => setActiveTab('benchmark')}
            style={{
              padding: '10px 18px',
              borderRadius: '8px',
              fontWeight: 600,
              backgroundColor: activeTab === 'benchmark' ? '#2e7d32' : 'transparent',
              color: activeTab === 'benchmark' ? '#ffffff' : '#64748b'
            }}
          >
            🧪 मॉडेल चाचणी (Evaluation Benchmark)
          </button>
        </div>
      </div>

      {/* Main Tab Content */}
      <main className="container">
        {activeTab === 'chat' && (
          <div>
            {/* Input Card */}
            <div className="card">
              <h2 style={{ fontSize: '1.15rem', color: '#166534', marginBottom: '14px', fontWeight: 700 }}>
                🎙️ आपला शेतीविषयक प्रश्न बोला किंवा टाईप करा (Speak or Type)
              </h2>

              {/* Voice Recorder Component */}
              <AudioRecorder onVoiceResult={handleVoiceResult} selectedLang={selectedLang} />

              <div style={{ display: 'flex', alignItems: 'center', margin: '16px 0', gap: '10px' }}>
                <div style={{ flex: 1, height: '1px', background: '#e2e8f0' }} />
                <span style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 600 }}>किंवा / OR</span>
                <div style={{ flex: 1, height: '1px', background: '#e2e8f0' }} />
              </div>

              {/* Text Input */}
              <div style={{ display: 'flex', gap: '10px' }}>
                <input
                  type="text"
                  placeholder="उदा. कापूस पिकात पाने पिवळी पडत आहेत काय उपाय करावा?"
                  value={queryText}
                  onChange={(e) => setQueryText(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleTextSearch()}
                  style={{
                    flex: 1,
                    padding: '14px 16px',
                    borderRadius: '10px',
                    border: '1px solid #cbd5e1',
                    fontSize: '1rem',
                  }}
                />
                <button
                  onClick={() => handleTextSearch()}
                  disabled={loading}
                  style={{
                    backgroundColor: '#1b5e20',
                    color: '#ffffff',
                    padding: '14px 24px',
                    borderRadius: '10px',
                    fontWeight: 600,
                    fontSize: '1rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <Search size={18} />
                  {loading ? 'शोधत आहे...' : 'उत्तर मिळवा'}
                </button>
              </div>

              {/* Quick Sample Prompts */}
              <div style={{ marginTop: '14px' }}>
                <span style={{ fontSize: '0.85rem', color: '#64748b', fontWeight: 600, marginRight: '8px' }}>
                  नमुना प्रश्न (Sample Questions):
                </span>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '8px' }}>
                  {samplePrompts.map((p, idx) => (
                    <button
                      key={idx}
                      onClick={() => {
                        setQueryText(p.text);
                        setSelectedLang(p.lang);
                        handleTextSearch(p.text);
                      }}
                      style={{
                        backgroundColor: '#f1f5f9',
                        color: '#334155',
                        padding: '6px 12px',
                        borderRadius: '20px',
                        fontSize: '0.85rem',
                        border: '1px solid #cbd5e1'
                      }}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Results Display */}
            {result && (
              <div className="card" style={{ marginTop: '20px' }}>
                {/* Status Badges */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', borderBottom: '1px solid #e2e8f0', paddingBottom: '14px' }}>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    {result.decision === 'answer' ? (
                      <span className="badge badge-green">
                        <ShieldCheck size={16} /> अधिकृत प्रमाणित उत्तर (Grounded)
                      </span>
                    ) : result.decision === 'warn_safety' ? (
                      <span className="badge badge-red">
                        <AlertTriangle size={16} /> कडक सुरक्षा इशारा (Chemical Hazard)
                      </span>
                    ) : (
                      <span className="badge badge-orange">
                        <HelpCircle size={16} /> सुरक्षित नकार व तज्ज्ञ मार्गदर्शन
                      </span>
                    )}
                    <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
                      विषय: <strong>{result.intent}</strong>
                    </span>
                  </div>

                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center', fontSize: '0.85rem', color: '#64748b' }}>
                    <span>विश्वासार्हता: <strong>{Math.round((result.overall_confidence || 0.9) * 100)}%</strong></span>
                    <span>गती: <strong>{result.latency_sec || 0.1}s</strong></span>
                  </div>
                </div>

                {/* Spoken Audio Response Player */}
                {result.audio_path && (
                  <div style={{ background: '#f8fafc', padding: '12px 16px', borderRadius: '10px', marginTop: '16px', display: 'flex', alignItems: 'center', gap: '14px', border: '1px solid #e2e8f0' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#166534', fontWeight: 600 }}>
                      <Volume2 size={20} />
                      बोलून दिलेले उत्तर (Spoken Audio):
                    </div>
                    <audio
                      controls
                      autoPlay
                      src={result.audio_path.startsWith('http') ? result.audio_path : `/api/audio/${result.audio_path.split(/[\\\\/]/).pop()}`}
                      style={{ height: '36px', flex: 1 }}
                    />
                  </div>
                )}

                {/* Answer Text */}
                <div style={{ marginTop: '16px', fontSize: '1.1rem', lineHeight: 1.7, color: '#1e293b' }}>
                  {result.answer_text.split('\n\n').map((para, i) => (
                    <p key={i} style={{ marginBottom: '10px' }}>{para}</p>
                  ))}
                </div>

                {/* Source Citation */}
                {result.source_name && result.source_name !== 'N/A' && (
                  <div style={{ marginTop: '14px', fontSize: '0.9rem', color: '#166534', fontWeight: 600, background: '#f0fdf4', padding: '8px 12px', borderRadius: '6px' }}>
                    🏛️ माहिती स्रोत: {result.source_name}
                  </div>
                )}

                {/* Evidence Passages Toggle */}
                {result.evidence_passages && result.evidence_passages.length > 0 && (
                  <div style={{ marginTop: '16px' }}>
                    <button
                      onClick={() => setShowEvidence(!showEvidence)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        background: 'transparent',
                        color: '#64748b',
                        fontSize: '0.85rem',
                        fontWeight: 600,
                        padding: '4px 0'
                      }}
                    >
                      {showEvidence ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                      {showEvidence ? 'प्रमाणित संदर्भ परिच्छेद लपवा' : 'प्रमाणित संदर्भ परिच्छेद पहा (Evidence Passages)'}
                    </button>

                    {showEvidence && (
                      <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', marginTop: '8px', border: '1px solid #e2e8f0', fontSize: '0.9rem', color: '#475569' }}>
                        {result.evidence_passages.map((p, idx) => (
                          <div key={idx} style={{ marginBottom: idx > 0 ? '8px' : '0', paddingBottom: idx < result.evidence_passages.length - 1 ? '8px' : '0', borderBottom: idx < result.evidence_passages.length - 1 ? '1px dashed #cbd5e1' : 'none' }}>
                            <strong>परिच्छेद {idx + 1}:</strong> {p}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'mandi' && <MandiTracker />}
        {activeTab === 'weather' && <WeatherAdvisory />}
        {activeTab === 'benchmark' && <BenchmarkView />}
      </main>
    </div>
  );
}
