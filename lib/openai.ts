/**
 * OpenAI Service
 */
import OpenAI from 'openai';
import { getConfig } from './config';

export interface ChatResponse {
  message: string;
  conversation_id?: string;
  agent_id?: string;
  citations?: any[];
}

let openaiClient: OpenAI | null = null;

function getOpenAIClient(): OpenAI {
  if (openaiClient) {
    return openaiClient;
  }

  const config = getConfig();
  
  if (!config.openai.apiKey) {
    throw new Error('OpenAI API key must be configured');
  }

  openaiClient = new OpenAI({
    apiKey: config.openai.apiKey,
  });

  return openaiClient;
}

export async function chatWithOpenAI(
  inputText: string,
  conversationId?: string
): Promise<ChatResponse> {
  try {
    const client = getOpenAIClient();
    const config = getConfig();

    const response = await client.chat.completions.create({
      model: config.openai.model,
      messages: [
        {
          role: 'system',
          content: 'You are a helpful security analyst assistant for Snort IDS alerts.',
        },
        {
          role: 'user',
          content: inputText,
        },
      ],
      max_tokens: config.openai.maxTokens,
      temperature: config.openai.temperature,
    });

    const message = response.choices[0]?.message?.content || '';

    return {
      message,
      conversation_id: conversationId || `openai_${Date.now()}`,
      agent_id: 'openai',
      citations: [],
    };
  } catch (error: any) {
    console.error('OpenAI API error:', error);
    throw new Error(`OpenAI API error: ${error.message}`);
  }
}
