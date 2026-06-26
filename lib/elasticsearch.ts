/**
 * Elasticsearch client for SnortAI
 */
import { Client } from '@elastic/elasticsearch';
import { getConfig } from './config';

let client: Client | null = null;

export function getElasticsearchClient(): Client {
  if (client) {
    return client;
  }

  const config = getConfig();
  
  if (!config.elasticsearch.url || !config.elasticsearch.apiKey) {
    throw new Error('Elasticsearch URL and API key must be configured');
  }

  // Ensure we're using the Elasticsearch endpoint, not Kibana
  let esUrl = config.elasticsearch.url;
  if (esUrl.includes('.kb.')) {
    esUrl = esUrl.replace('.kb.', '.es.');
    console.log(`Converted Kibana URL to Elasticsearch URL: ${esUrl}`);
  }

  client = new Client({
    node: esUrl,
    auth: {
      apiKey: config.elasticsearch.apiKey,
    },
  });

  // Ensure index exists (async, but don't wait)
  ensureIndex(client, config.elasticsearch.index).catch(err => {
    console.error('Failed to ensure index exists:', err);
  });

  return client;
}

async function ensureIndex(esClient: Client, indexName: string) {
  try {
    const exists = await esClient.indices.exists({ index: indexName });
    
    if (!exists) {
      console.log(`Creating Elasticsearch index: ${indexName}`);
      await esClient.indices.create({
        index: indexName,
        mappings: {
          properties: {
            timestamp: { type: 'date' },
            alert_type: { type: 'keyword' },
            priority: { type: 'integer' },
            protocol: { type: 'keyword' },
            source_ip: { type: 'ip' },
            source_port: { type: 'integer' },
            destination_ip: { type: 'ip' },
            destination_port: { type: 'integer' },
            message: { type: 'text' },
            classification: { type: 'keyword' },
            signature_id: { type: 'keyword' },
            raw_alert: { type: 'text' },
            analysis: { type: 'text' },
            recommendations: { type: 'text' },
            confidence_score: { type: 'float' },
          },
        },
      });
      console.log(`Successfully created index: ${indexName}`);
    } else {
      console.log(`Index ${indexName} already exists`);
    }
  } catch (error: any) {
    console.error('Error ensuring Elasticsearch index:', error);
    console.error('Index name:', indexName);
    console.error('Error details:', error.message);
  }
}

export async function storeAlert(alertData: Record<string, any>): Promise<boolean> {
  try {
    const esClient = getElasticsearchClient();
    const config = getConfig();
    
    const response = await esClient.index({
      index: config.elasticsearch.index,
      document: alertData,
    });
    
    return response.result === 'created' || response.result === 'updated';
  } catch (error) {
    console.error('Error storing alert in Elasticsearch:', error);
    return false;
  }
}

export async function searchAlerts(query: Record<string, any>): Promise<any[]> {
  try {
    const config = getConfig();
    
    if (!config.elasticsearch.url || !config.elasticsearch.apiKey) {
      console.warn('Elasticsearch not configured, returning empty array');
      return [];
    }
    
    const esClient = getElasticsearchClient();
    
    const response = await esClient.search({
      index: config.elasticsearch.index,
      body: query,
    });
    
    const hits = response.hits?.hits || [];
    console.log(`Elasticsearch search returned ${hits.length} documents`);
    
    return hits.map((hit: any) => hit._source);
  } catch (error: any) {
    console.error('Error searching alerts in Elasticsearch:', error);
    console.error('Error details:', {
      message: error.message,
      name: error.name,
      statusCode: error.statusCode,
      meta: error.meta,
    });
    return [];
  }
}

export async function getAlertStats(): Promise<Record<string, any>> {
  try {
    const esClient = getElasticsearchClient();
    const config = getConfig();
    
    const response = await esClient.search({
      index: config.elasticsearch.index,
      body: {
        size: 0,
        aggs: {
          alert_types: { terms: { field: 'alert_type' } },
          priority_distribution: { terms: { field: 'priority' } },
          total_alerts: { value_count: { field: '_id' } },
        },
      },
    });
    
    const aggs = response.aggregations as any;
    
    return {
      total_alerts: aggs?.total_alerts?.value || 0,
      alert_types: aggs?.alert_types?.buckets || [],
      priority_distribution: aggs?.priority_distribution?.buckets || [],
    };
  } catch (error) {
    console.error('Error getting alert stats from Elasticsearch:', error);
    return {};
  }
}
