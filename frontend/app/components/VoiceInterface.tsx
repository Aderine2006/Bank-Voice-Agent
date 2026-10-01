'use client';

import { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Volume2, VolumeX } from 'lucide-react';

interface VoiceInterfaceProps {
  onTranscript: (transcript: string) => void;
  isListening: boolean;
  onToggleListening: () => void;
}

export default function VoiceInterface({
  onTranscript,
  isListening,
  onToggleListening,
}: VoiceInterfaceProps) {
  const [audioLevel, setAudioLevel] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationRef = useRef<number>();

  useEffect(() => {
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, []);

  const startListening = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      audioContextRef.current = new AudioContext();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      analyserRef.current.fftSize = 256;

      mediaRecorderRef.current = new MediaRecorder(stream);
      const chunks: Blob[] = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        chunks.push(e.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/wav' });
        
        // Send to backend for transcription
        try {
          const { transcribeAudio } = await import('../lib/api');
          const transcript = await transcribeAudio(audioBlob);
          onTranscript(transcript);
        } catch (error) {
          console.error('Transcription error:', error);
        }

        // Stop all tracks
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current.start();
      
      // Animate audio level
      const animate = () => {
        if (!analyserRef.current) return;
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
        setAudioLevel(average / 255);
        animationRef.current = requestAnimationFrame(animate);
      };
      animate();

    } catch (error) {
      console.error('Microphone error:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };

  const stopListening = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    setAudioLevel(0);
  };

  const handleToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
    onToggleListening();
  };

  return (
    <div className="flex flex-col items-center gap-6">
      {/* Voice Waveform */}
      <div className="flex items-center justify-center gap-1 h-16">
        {[...Array(5)].map((_, i) => (
          <div
            key={i}
            className="w-1 bg-primary-500 rounded-full transition-all duration-150"
            style={{
              height: isListening
                ? `${20 + audioLevel * 60 * (1 - Math.abs(i - 2) * 0.3)}px`
                : '8px',
              opacity: isListening ? 1 : 0.3,
            }}
          />
        ))}
      </div>

      {/* Microphone Button */}
      <button
        onClick={handleToggle}
        className={`relative w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 ${
          isListening
            ? 'bg-red-500 hover:bg-red-600 scale-110'
            : 'bg-primary-600 hover:bg-primary-700 hover:scale-105'
        }`}
      >
        {isListening ? (
          <MicOff className="w-8 h-8 text-white" />
        ) : (
          <Mic className="w-8 h-8 text-white" />
        )}
      </button>

      <p className="text-sm text-gray-400">
        {isListening ? 'Listening...' : 'Tap to speak'}
      </p>
    </div>
  );
}
