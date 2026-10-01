const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ConversationState {
  conversation_id: string;
  current_stage: string;
  intent: string;
  customer_profile: any;
  missing_fields: string[];
  candidate_products: string[];
  eligible_products: string[];
  ineligible_products: string[];
}

export interface ConversationResponse {
  conversation_id: string;
  transcript: string;
  intent: string;
  assistant_response: string;
  profile_updates: any;
  missing_information: string[];
  loan_matches: any[];
  workflow_stage: string;
  audio_url?: string;
  sources: any[];
}

export interface LoanProduct {
  product_id: string;
  product_name: string;
  loan_type: string;
  purpose: string;
  minimum_amount: number;
  maximum_amount: number;
  interest_rate_range: string;
  processing_fee: string;
  required_documents: string[];
}

export async function startConversation(): Promise<ConversationState> {
  const response = await fetch(`${API_BASE}/api/conversation/start`, {
    method: 'POST',
  });
  if (!response.ok) throw new Error('Failed to start conversation');
  return response.json();
}

export async function sendMessage(
  conversationId: string,
  message: string
): Promise<ConversationResponse> {
  const response = await fetch(`${API_BASE}/api/conversation/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      conversation_id: conversationId,
      message,
    }),
  });
  if (!response.ok) throw new Error('Failed to send message');
  return response.json();
}

export async function getProducts(): Promise<LoanProduct[]> {
  const response = await fetch(`${API_BASE}/api/products`);
  if (!response.ok) throw new Error('Failed to fetch products');
  return response.json();
}

export async function transcribeAudio(audioBlob: Blob): Promise<string> {
  const formData = new FormData();
  formData.append('audio_file', audioBlob, 'audio.wav');

  const response = await fetch(`${API_BASE}/api/voice/transcribe`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to transcribe audio');
  const data = await response.json();
  return data.transcript;
}

export async function synthesizeSpeech(text: string): Promise<Blob> {
  const response = await fetch(
    `${API_BASE}/api/voice/synthesize?text=${encodeURIComponent(text)}`,
    {
      method: 'POST',
    }
  );
  if (!response.ok) throw new Error('Failed to synthesize speech');
  return response.blob();
}
