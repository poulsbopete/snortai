/**
 * MCP Server status endpoint
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
    const tools = await mcpService.getTools();

    return res.status(200).json({
      status: 'healthy',
      agents_count: agents.length,
      tools_count: tools.length,
      available_agents: agents.map((agent: any) => ({
        id: agent.id,
        name: agent.name,
      })),
      timestamp: new Date().toISOString(),
    });
  } catch (error: any) {
    console.error('MCP server status check failed:', error);
    // Always return 200 with unhealthy status instead of throwing
    return res.status(200).json({
      status: 'unhealthy',
      error: error?.message || 'Unknown error',
      agents_count: 0,
      tools_count: 0,
      available_agents: [],
      timestamp: new Date().toISOString(),
    });
  }
}
