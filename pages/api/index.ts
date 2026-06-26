/**
 * Root API endpoint
 */
import type { NextApiRequest, NextApiResponse } from 'next';

export default function handler(req: NextApiRequest, res: NextApiResponse) {
  res.status(200).json({
    message: 'Snort AI Assistant API',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/api/mcp/status',
      alerts: '/api/alerts',
      chat: '/api/mcp/converse',
    },
  });
}
