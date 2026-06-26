/**
 * AI Assistant endpoint with backend switching
 */
import type { NextApiRequest, NextApiResponse } from 'next';
import { getMCPServerService } from '../../lib/mcp-server';
import { chatWithOpenAI } from '../../lib/openai';
import { getConfig } from '../../lib/config';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { question, backend } = req.body;

    if (!question) {
      return res.status(400).json({ error: 'Question is required' });
    }

    const config = getConfig();
    const backendToUse = backend || config.aiBackend.type;

    let response;

    try {
      if (backendToUse === 'mcp') {
        const mcpService = getMCPServerService();
        // Always use the 'snortai' agent for MCP server
        response = await mcpService.chat(question, undefined, 'snortai');
      } else {
        response = await chatWithOpenAI(question);
      }
    } catch (error: any) {
      // Fallback to other backend if configured
      if (config.aiBackend.fallback) {
        try {
          if (backendToUse === 'mcp') {
            response = await chatWithOpenAI(question);
          } else {
            const mcpService = getMCPServerService();
            // Always use the 'snortai' agent for MCP server fallback
            response = await mcpService.chat(question, undefined, 'snortai');
          }
        } catch (fallbackError: any) {
          return res.status(500).json({
            answer: 'Sorry, I couldn\'t get an answer from the AI assistant.',
            citations: [],
            error: fallbackError.message,
            backend_used: backendToUse,
          });
        }
      } else {
        throw error;
      }
    }

    res.status(200).json({
      answer: response.message,
      citations: response.citations || [],
      conversation_id: response.conversation_id,
      backend_used: backendToUse,
    });
  } catch (error: any) {
    console.error('AI assistant error:', error);
    res.status(500).json({
      answer: 'Sorry, I couldn\'t get an answer from the AI assistant.',
      citations: [],
      error: error.message,
    });
  }
}
