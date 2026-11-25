import React, { useState, useRef } from 'react';
import { Mic, Square, Upload, Loader2, Volume2 } from 'lucide-react';

export default function AudioRecorder({ onVoiceResult, selectedLang }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await sendAudioToServer(audioBlob, 'voice_query.wav');
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordingTime(0);

      timerRef.current = setInterval(() => {
        setRecordingTime((prev) => {
          if (prev >= 30) {
            stopRecording();
            return 30;
          }
          return prev + 1;
        });
      }, 1000);
    } catch (err) {
      alert("Microphone permission denied or not available. Please allow mic access or use file upload.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (file) {
      await sendAudioToServer(file, file.name);
    }
  };

  const sendAudioToServer = async (blobOrFile, filename) => {
    setIsLoading(true);
    const formData = new FormData();
    formData.append('audio_file', blobOrFile, filename);
    if (selectedLang) {
      formData.append('language', selectedLang);
    }

    try {
      const response = await fetch('/api/voice', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      onVoiceResult(data);
    } catch (err) {
      alert("Error sending voice note to backend: " + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
        {!isRecording ? (
          <button
            onClick={startRecording}
            disabled={isLoading}
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '10px',
              backgroundColor: '#2e7d32',
              color: '#ffffff',
              padding: '14px 20px',
              borderRadius: '10px',
              fontSize: '1rem',
              fontWeight: '600',
              opacity: isLoading ? 0.7 : 1,
            }}
          >
            {isLoading ? <Loader2 size={20} className="spin" /> : <Mic size={22} />}
            {isLoading ? 'प्रक्रिया सुरू आहे... / Processing...' : 'माझा प्रश्न बोला (Record Voice)'}
          </button>
        ) : (
          <button
            onClick={stopRecording}
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '10px',
              backgroundColor: '#c62828',
              color: '#ffffff',
              padding: '14px 20px',
              borderRadius: '10px',
              fontSize: '1rem',
              fontWeight: '600',
              animation: 'pulse 1.5s infinite',
            }}
          >
            <Square size={20} />
            थांबवा / Stop ({recordingTime}s / 30s)
          </button>
        )}

        <label
          style={{
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            backgroundColor: '#ffffff',
            border: '1px solid #cbd5e1',
            color: '#334155',
            padding: '14px 18px',
            borderRadius: '10px',
            fontWeight: '600',
          }}
        >
          <Upload size={18} />
          WhatsApp Audio Upload
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            disabled={isLoading || isRecording}
          />
        </label>
      </div>

      {isRecording && (
        <div style={{ color: '#c62828', fontSize: '0.9rem', textAlign: 'center', fontWeight: '500' }}>
          🔴 आवाज रेकॉर्ड होत आहे... कृपया आपला शेतीविषयक प्रश्न स्पष्ट आवाजात विचारा.
        </div>
      )}
    </div>
  );
}
