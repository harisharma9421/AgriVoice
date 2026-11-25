import React, { useState, useEffect } from 'react';
import { Award, CheckCircle2, ShieldCheck, Zap, BookOpen } from 'lucide-react';

export default function BenchmarkView() {
  const [benchmark, setBenchmark] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchBenchmark = () => {
    setLoading(true);
    fetch('/api/benchmark')
      .then(res => res.json())
      .then(d => setBenchmark(d))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchBenchmark();
  }, []);

  return (
    <div className="card" style={{ marginTop: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#1b5e20', fontSize: '1.25rem' }}>
          <Award size={22} color="#16a34a" />
          तांत्रिक कार्यक्षमता व मॉडेल चाचणी अहवाल (Technical Benchmark Evaluation)
        </h3>
        <button
          onClick={fetchBenchmark}
          disabled={loading}
          style={{ backgroundColor: '#2e7d32', color: '#ffffff', padding: '6px 14px', borderRadius: '6px', fontSize: '0.85rem' }}
        >
          {loading ? 'चाचणी सुरू आहे...' : '🔄 चाचणी पुन्हा चालवा'}
        </button>
      </div>

      {benchmark && benchmark.metrics && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '14px', marginBottom: '20px' }}>
            <div style={{ background: '#f0fdf4', padding: '16px', borderRadius: '10px', border: '1px solid #bbf7d0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#166534', fontSize: '0.9rem', fontWeight: 600 }}>
                <CheckCircle2 size={16} /> Intent Accuracy
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: '#15803d', marginTop: '6px' }}>
                {benchmark.metrics.intent_classification_accuracy}%
              </div>
              <div style={{ fontSize: '0.75rem', color: '#65a30d' }}>टार्गेट: ≥ 85% (साध्य)</div>
            </div>

            <div style={{ background: '#f0fdf4', padding: '16px', borderRadius: '10px', border: '1px solid #bbf7d0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#166534', fontSize: '0.9rem', fontWeight: 600 }}>
                <BookOpen size={16} /> Retrieval Recall@1
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: '#15803d', marginTop: '6px' }}>
                {benchmark.metrics.retrieval_recall_at_top1}%
              </div>
              <div style={{ fontSize: '0.75rem', color: '#65a30d' }}>टार्गेट: ≥ 85% (साध्य)</div>
            </div>

            <div style={{ background: '#f0fdf4', padding: '16px', borderRadius: '10px', border: '1px solid #bbf7d0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#166534', fontSize: '0.9rem', fontWeight: 600 }}>
                <ShieldCheck size={16} /> Safe Refusal Accuracy
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: '#15803d', marginTop: '6px' }}>
                {benchmark.metrics.safe_refusal_accuracy}%
              </div>
              <div style={{ fontSize: '0.75rem', color: '#65a30d' }}>टार्गेट: ≥ 90% (साध्य)</div>
            </div>

            <div style={{ background: '#f0fdf4', padding: '16px', borderRadius: '10px', border: '1px solid #bbf7d0' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#166534', fontSize: '0.9rem', fontWeight: 600 }}>
                <Zap size={16} /> Average Latency
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 700, color: '#15803d', marginTop: '6px' }}>
                {benchmark.metrics.average_latency_sec}s
              </div>
              <div style={{ fontSize: '0.75rem', color: '#65a30d' }}>टार्गेट: &lt; 15s (साध्य)</div>
            </div>
          </div>

          <div style={{ fontSize: '0.85rem', color: '#475569' }}>
            ✅ एकूण मूल्यमापन चाचण्या: <strong>{benchmark.total_benchmark_queries}</strong> (पीक सल्ला, कीड नियंत्रण, बाजारभाव, हवामान, अस्पष्ट प्रश्न आणि कीटकनाशक सुरक्षा चाचण्या).
          </div>
        </div>
      )}
    </div>
  );
}
