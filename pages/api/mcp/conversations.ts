/**
 * MCP Server conversations endpoint
 */
import type { NextApiRequest, NextApiResponse } from 'next';
import { getMCPServerService } from '../../../lib/mcp-server';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const mcpService = getMCPServerService();
    const conversations = await mcpService.getConversations();
    
    return res.status(200).json({ conversations });
  } catch (error: any) {
    console.error('Failed to get MCP server conversations:', error);
    // Always return 200 with empty array instead of error
    return res.status(200).json({ conversations: [] });
  }
}
