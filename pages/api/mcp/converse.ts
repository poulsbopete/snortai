/**
 * MCP Server conversation endpoint
 */
import type { NextApiRequest, NextApiResponse } from 'next';
import { getMCPServerService } from '../../../lib/mcp-server';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { input, conversation_id, agent_id, connector_id } = req.body;

    if (!input) {
      return res.status(400).json({ error: 'Input text is required' });
    }

    const mcpService = getMCPServerService();
    // Default to 'snortai' agent if not specified
    const agentIdToUse = agent_id || 'snortai';
    const response = await mcpService.chat(input, conversation_id, agentIdToUse, connector_id);

    res.status(200).json({
      message: response.message,
      conversation_id: response.conversation_id,
      agent_id: response.agent_id,
      citations: response.citations || [],
    });
  } catch (error: any) {
    console.error('Failed to converse with MCP server:', error);
    res.status(500).json({ error: 'Failed to get response from MCP server' });
  }
}
