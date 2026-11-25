import React, { useState, useEffect } from 'react';
import { CloudRain, Wind, Droplets, Sun, AlertTriangle } from 'lucide-react';

export default function WeatherAdvisory() {
  const [district, setDistrict] = useState('nagpur');
  const [weather, setWeather] = useState(null);

  useEffect(() => {
    fetch(`/api/weather?district=${district}&lang=mr`)
      .then(res => res.json())
      .then(d => setWeather(d))
      .catch(console.error);
  }, [district]);

  return (
    <div className="card" style={{ marginTop: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#1b5e20', fontSize: '1.25rem' }}>
          <Sun size={22} color="#eab308" />
          हवामान आणि कृषी ॲग्रोमेट सल्ला (IMD Agromet Advisory)
        </h3>
        <select
          value={district}
          onChange={(e) => setDistrict(e.target.value)}
          style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.9rem' }}
        >
          <option value="nagpur">नागपूर (Nagpur)</option>
          <option value="pune">पुणे (Pune)</option>
          <option value="nashik">नाशिक (Nashik)</option>
          <option value="indore">इंदूर (Indore)</option>
        </select>
      </div>

      {weather && weather.success && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px', marginBottom: '16px' }}>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <Sun size={20} color="#eab308" style={{ margin: '0 auto' }} />
              <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '4px' }}>तापमान</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>{weather.temp_c}°C</div>
            </div>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <CloudRain size={20} color="#0284c7" style={{ margin: '0 auto' }} />
              <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '4px' }}>पाऊस शक्यता</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>{weather.rain_prob}</div>
            </div>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <Droplets size={20} color="#06b6d4" style={{ margin: '0 auto' }} />
              <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '4px' }}>हवेतील आर्द्रता</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>{weather.humidity}</div>
            </div>
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '8px', textAlign: 'center' }}>
              <Wind size={20} color="#64748b" style={{ margin: '0 auto' }} />
              <div style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '4px' }}>वाऱ्याचा वेग</div>
              <div style={{ fontSize: '1.3rem', fontWeight: 700 }}>{weather.wind_kmh} km/h</div>
            </div>
          </div>

          <div style={{ background: '#f0fdf4', padding: '14px', borderRadius: '8px', borderLeft: '4px solid #22c55e', fontSize: '0.95rem', color: '#166534', lineHeight: 1.6 }}>
            📢 <strong>शेतकरी सल्ला:</strong> {weather.formatted_response}
          </div>
        </div>
      )}
    </div>
  );
}
