'use client';

import { useState, useEffect } from 'react';
import VoiceInterface from './components/VoiceInterface';
import ConversationPanel from './components/ConversationPanel';
import ProfileCard from './components/ProfileCard';
import LoanMatches from './components/LoanMatches';
import Dashboard from './components/Dashboard';
import { startConversation, sendMessage, synthesizeSpeech } from './lib/api';
import { RefreshCw, Volume2 } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

export default function Home() {
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [conversationState, setConversationState] = useState<any>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    initializeConversation();
  }, []);

  const initializeConversation = async () => {
    try {
      const state = await startConversation();
      setConversationId(state.conversation_id);
      setConversationState(state);
      
      // Add greeting message
      setMessages([
        {
          role: 'assistant',
          content: "Hi, I'm Ava, the bank's virtual assistant. I can help you explore loan options and understand the information required. How can I help you today?",
        },
      ]);
    } catch (error) {
      console.error('Failed to start conversation:', error);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!conversationId) return;

    setIsLoading(true);
    
    // Add user message
    setMessages((prev) => [...prev, { role: 'user', content: message }]);

    try {
      const response = await sendMessage(conversationId, message);
      
      // Add assistant response
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.assistant_response },
      ]);

      // Update conversation state
      setConversationState({
        ...response,
        current_stage: response.workflow_stage,
      });

      // Synthesize speech
      try {
        const audioBlob = await synthesizeSpeech(response.assistant_response);
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        setIsPlaying(true);
        audio.onended = () => setIsPlaying(false);
        audio.play();
      } catch (error) {
        console.error('TTS error:', error);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTranscript = (transcript: string) => {
    if (transcript.trim()) {
      handleSendMessage(transcript);
    }
  };

  const handleReset = async () => {
    setMessages([]);
    setConversationState(null);
    await initializeConversation();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-950/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <span className="text-white font-bold text-lg">BV</span>
            </div>
            <div>
              <h1 className="text-xl font-bold gradient-text">BankVoice AI</h1>
              <p className="text-xs text-gray-500">Conversational Banking Assistant</p>
            </div>
          </div>
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            Reset
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Voice & Conversation */}
          <div className="lg:col-span-2 space-y-6">
            {/* Voice Interface */}
            <div className="glass-card p-8">
              <div className="text-center mb-6">
                <h2 className="text-2xl font-bold gradient-text mb-2">Speak with Ava</h2>
                <p className="text-sm text-gray-500">
                  Your virtual banking assistant
                </p>
              </div>
              <VoiceInterface
                onTranscript={handleTranscript}
                isListening={isListening}
                onToggleListening={() => setIsListening(!isListening)}
              />
            </div>

            {/* Conversation Panel */}
            <div className="glass-card h-[500px]">
              <ConversationPanel
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isLoading}
              />
            </div>
          </div>

          {/* Right Column - Dashboard & Info */}
          <div className="space-y-6">
            {/* Dashboard */}
            <Dashboard conversationState={conversationState} />

            {/* Profile Card */}
            <ProfileCard profile={conversationState?.profile_updates || {}} />

            {/* Loan Matches */}
            <LoanMatches matches={conversationState?.loan_matches || []} />

            {/* Speaking Indicator */}
            {isPlaying && (
              <div className="glass-card p-4 flex items-center gap-3">
                <Volume2 className="w-5 h-5 text-primary-500 animate-pulse" />
                <span className="text-sm text-gray-300">Ava is speaking...</span>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-gray-500">
          <p>BANKVOICE AI - Demo / Fictional Bank Data</p>
          <p className="mt-1 text-xs">
            All rates, policies, and products are fictional examples for demonstration purposes only.
          </p>
        </div>
      </footer>
    </div>
  );
}
