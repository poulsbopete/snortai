/**
 * Get alerts from Elasticsearch
 */
import type { NextApiRequest, NextApiResponse } from 'next';
import { searchAlerts } from '../../lib/elasticsearch';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { start_time, end_time, alert_type, priority } = req.query;

    const query: any = {
      query: {
        bool: {
          must: [],
        },
      },
      sort: [{ timestamp: { order: 'desc' } }],
      size: 100,
    };

    if (start_time) {
      query.query.bool.must.push({
        range: { timestamp: { gte: start_time } },
      });
    }

    if (end_time) {
      query.query.bool.must.push({
        range: { timestamp: { lte: end_time } },
      });
    }

    if (alert_type) {
      query.query.bool.must.push({
        term: { alert_type: alert_type },
      });
    }

    if (priority) {
      query.query.bool.must.push({
        term: { priority: parseInt(priority as string, 10) },
      });
    }

    const alerts = await searchAlerts(query);
    console.log(`API /alerts: Returning ${alerts.length} alerts`);
    return res.status(200).json(alerts);
  } catch (error: any) {
    console.error('Error searching alerts:', error);
    console.error('Error stack:', error.stack);
    // Return empty array instead of error to prevent 404
    return res.status(200).json([]);
  }
}
