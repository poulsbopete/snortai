/**
 * MCP Server tools endpoint
 */
import type { NextApiRequest, NextApiResponse } from 'next';
import { getMCPServerService } from '../../../lib/mcp-server';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const mcpService = getMCPServerService();
    const tools = await mcpService.getTools();
    
    res.status(200).json({ tools });
  } catch (error: any) {
    console.error('Failed to get MCP server tools:', error);
    res.status(500).json({ error: 'Failed to get tools', tools: [] });
  }
}
