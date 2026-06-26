/**
 * Get alert statistics
 */
import type { NextApiRequest, NextApiResponse } from 'next';
import { getAlertStats } from '../../lib/elasticsearch';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const stats = await getAlertStats();
    res.status(200).json(stats);
  } catch (error: any) {
    console.error('Error getting alert stats:', error);
    res.status(500).json({ error: 'Failed to get alert stats' });
  }
}
