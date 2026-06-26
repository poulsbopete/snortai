/**
 * MCP Server agents endpoint
 */
import type { NextApiRequest, NextApiResponse } from 'next';
import { getMCPServerService } from '../../../lib/mcp-server';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const mcpService = getMCPServerService();
    const agents = await mcpService.getAgents();
    
    return res.status(200).json({
      agents: agents.map((agent: any) => ({
        id: agent.id,
        name: agent.name,
        description: agent.description,
      })),
    });
  } catch (error: any) {
    console.error('Failed to get MCP server agents:', error);
    // Always return 200 with empty array instead of error
    return res.status(200).json({ agents: [] });
  }
}
