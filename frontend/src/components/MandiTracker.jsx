import React, { useState, useEffect } from 'react';
import { TrendingUp, RefreshCw, MapPin } from 'lucide-react';

export default function MandiTracker() {
  const [commodity, setCommodity] = useState('कापूस');
  const [market, setMarket] = useState('Nagpur');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchRates = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/mandi?commodity=${encodeURIComponent(commodity)}&market=${encodeURIComponent(market)}&lang=mr`);
      const result = await res.json();
      setData(result);
    } catch (err) {
      console.error("Error fetching mandi data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRates();
  }, [commodity, market]);

  return (
    <div className="card" style={{ marginTop: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#1b5e20', fontSize: '1.25rem' }}>
          <TrendingUp size={22} />
          थेट बाजारभाव माहिती (Agmarknet / e-NAM Mandi Prices)
        </h3>
        <button
          onClick={fetchRates}
          disabled={loading}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            backgroundColor: '#f1f5f9',
            padding: '6px 12px',
            borderRadius: '6px',
            fontSize: '0.85rem',
            color: '#475569'
          }}
        >
          <RefreshCw size={14} /> ताजे दर
        </button>
      </div>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '200px' }}>
          <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#64748b', display: 'block', marginBottom: '6px' }}>
            शेतमाल / Commodity:
          </label>
          <select
            value={commodity}
            onChange={(e) => setCommodity(e.target.value)}
            style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '1rem' }}
          >
            <option value="कापूस">कापूस (Cotton)</option>
            <option value="सोयाबीन">सोयाबीन (Soybean)</option>
            <option value="गहू">गहू (Wheat)</option>
            <option value="टोमॅटो">टोमॅटो (Tomato)</option>
            <option value="कांदा">कांदा (Onion)</option>
            <option value="हरभरा">हरभरा (Gram / Chana)</option>
          </select>
        </div>

        <div style={{ flex: 1, minWidth: '200px' }}>
          <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#64748b', display: 'block', marginBottom: '6px' }}>
            बाजार समिती / Mandi:
          </label>
          <select
            value={market}
            onChange={(e) => setMarket(e.target.value)}
            style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '1rem' }}
          >
            <option value="Nagpur">नागपूर (Nagpur)</option>
            <option value="Akola">अकोला (Akola)</option>
            <option value="Pune">पुणे (Pune)</option>
            <option value="Nashik">नाशिक (Nashik)</option>
            <option value="Lasalgaon">लासलगाव (Lasalgaon)</option>
            <option value="Indore">इंदूर (Indore)</option>
            <option value="Karnal">कर्नाल (Karnal)</option>
          </select>
        </div>
      </div>

      {data && data.success && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px', marginBottom: '16px' }}>
            <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '10px', textAlign: 'center', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>सरासरी दर (Modal)</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#166534', marginTop: '4px' }}>₹{data.modal_price}</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>प्रति क्विंटल</div>
            </div>
            <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '10px', textAlign: 'center', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>किमान दर (Min)</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#0f172a', marginTop: '4px' }}>₹{data.min_price}</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>प्रति क्विंटल</div>
            </div>
            <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '10px', textAlign: 'center', border: '1px solid #e2e8f0' }}>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>कमाल दर (Max)</div>
              <div style={{ fontSize: '1.6rem', fontWeight: 700, color: '#0f172a', marginTop: '4px' }}>₹{data.max_price}</div>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>प्रति क्विंटल</div>
            </div>
          </div>
          <div style={{ fontSize: '0.9rem', color: '#334155', background: '#ecfdf5', padding: '10px 14px', borderRadius: '8px', borderLeft: '4px solid #10b981' }}>
            📅 <strong>माहिती दिनांक:</strong> {data.as_of_date} | 📍 <strong>बाजार:</strong> {data.market} | 🚚 <strong>आवक:</strong> {data.arrivals_tonnes} टन
          </div>
        </div>
      )}
    </div>
  );
}
