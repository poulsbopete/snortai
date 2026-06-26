/**
 * Debug endpoint to check Elasticsearch connection and data
 */
import type { NextApiRequest, NextApiResponse } from 'next';
import { getElasticsearchClient, searchAlerts } from '../../../lib/elasticsearch';
import { getConfig } from '../../../lib/config';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const config = getConfig();
    
    const debugInfo: any = {
      config: {
        elasticsearch_url: config.elasticsearch.url ? '***configured***' : 'NOT SET',
        elasticsearch_index: config.elasticsearch.index,
        api_key_set: config.elasticsearch.apiKey ? '***set***' : 'NOT SET',
      },
      connection_test: null,
      index_exists: null,
      document_count: null,
      sample_query: null,
      error: null,
    };

    // Test connection
    try {
      if (!config.elasticsearch.url || !config.elasticsearch.apiKey) {
        debugInfo.error = 'Elasticsearch URL or API key not configured';
        return res.status(200).json(debugInfo);
      }

      const esClient = getElasticsearchClient();
      
      // Test connection with a simple ping
      try {
        await esClient.ping();
        debugInfo.connection_test = 'SUCCESS';
      } catch (pingError: any) {
        debugInfo.connection_test = `FAILED: ${pingError.message}`;
        debugInfo.error = pingError.message;
        return res.status(200).json(debugInfo);
      }

      // Check if index exists
      try {
        const exists = await esClient.indices.exists({ index: config.elasticsearch.index });
        debugInfo.index_exists = exists;
      } catch (indexError: any) {
        debugInfo.index_exists = `ERROR: ${indexError.message}`;
      }

      // Get document count
      try {
        const countResponse = await esClient.count({ index: config.elasticsearch.index });
        debugInfo.document_count = countResponse.count;
      } catch (countError: any) {
        debugInfo.document_count = `ERROR: ${countError.message}`;
      }

      // Try a sample query
      try {
        const sampleQuery = {
          query: { match_all: {} },
          size: 5,
          sort: [{ timestamp: { order: 'desc' } }],
        };
        const results = await searchAlerts(sampleQuery);
        debugInfo.sample_query = {
          returned_count: results.length,
          sample_documents: results.slice(0, 2),
        };
      } catch (queryError: any) {
        debugInfo.sample_query = `ERROR: ${queryError.message}`;
      }

    } catch (error: any) {
      debugInfo.error = error.message;
      debugInfo.stack = error.stack;
    }

    return res.status(200).json(debugInfo);
  } catch (error: any) {
    console.error('Debug endpoint error:', error);
    return res.status(500).json({
      error: error.message,
      stack: error.stack,
    });
  }
}
