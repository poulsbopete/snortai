/**
 * Configuration management for SnortAI API
 */

export interface Config {
  elasticsearch: {
    url: string;
    apiKey: string;
    index: string;
  };
  openai: {
    apiKey: string;
    model: string;
    maxTokens: number;
    temperature: number;
  };
  aiBackend: {
    type: 'openai' | 'mcp';
    fallback: boolean;
    defaultAgentId?: string; // Default agent ID for MCP server
  };
  debug: boolean;
}

export function getConfig(): Config {
  return {
    elasticsearch: {
      url: (() => {
        const url = process.env.ELASTICSEARCH_URL || 'https://ai-assistants-ffcafb.kb.us-east-1.aws.elastic.cloud';
        // Convert Kibana URL (.kb.) to Elasticsearch URL (.es.) if needed
        if (url.includes('.kb.')) {
          return url.replace('.kb.', '.es.');
        }
        return url;
      })(),
      apiKey: process.env.ELASTICSEARCH_API_KEY || '',
      index: process.env.ELASTICSEARCH_INDEX || 'snort-alerts',
    },
    openai: {
      apiKey: process.env.OPENAI_API_KEY || '',
      model: process.env.OPENAI_MODEL || 'gpt-4o-mini',
      maxTokens: parseInt(process.env.OPENAI_MAX_TOKENS || '2000', 10),
      temperature: parseFloat(process.env.OPENAI_TEMPERATURE || '0.1'),
    },
    aiBackend: {
      type: (process.env.AI_BACKEND || 'openai') as 'openai' | 'mcp',
      fallback: process.env.AI_BACKEND_FALLBACK?.toLowerCase() === 'true',
      defaultAgentId: process.env.MCP_DEFAULT_AGENT_ID || 'snortai',
    },
    debug: process.env.DEBUG?.toLowerCase() === 'true',
  };
}
