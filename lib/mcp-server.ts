/**
 * Elastic MCP Server Service
 * Provides integration with Elastic's MCP (Model Context Protocol) server endpoint
 */
import axios, { AxiosInstance } from 'axios';
import { getConfig } from './config';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  agent_id?: string;
  citations?: any[];
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  configuration: Record<string, any>;
}

export class MCPServerService {
  private baseUrl: string;
  private apiKey: string;
  private axiosInstance: AxiosInstance;
  private agentsCache: Agent[] = [];
  private toolsCache: any[] = [];
  private cacheTimestamp: number = 0;
  private cacheTtl: number = 300000; // 5 minutes

  constructor() {
    const config = getConfig();
    
    // Convert Elasticsearch URL to Kibana URL for MCP API if needed
    let baseUrl = config.elasticsearch.url || 'https://ai-assistants-ffcafb.kb.us-east-1.aws.elastic.cloud';
    if (baseUrl.includes('.es.')) {
      baseUrl = baseUrl.replace('.es.', '.kb.');
    }
    
    this.baseUrl = baseUrl;
    this.apiKey = config.elasticsearch.apiKey || '';
    
    this.axiosInstance = axios.create({
      baseURL: this.baseUrl,
      headers: {
        'Authorization': this.apiKey ? `ApiKey ${this.apiKey}` : '',
        'Content-Type': 'application/json',
        'kbn-xsrf': 'true',
      },
      timeout: 60000,
    });
  }

  async getAgents(): Promise<Agent[]> {
    const now = Date.now();
    if (this.agentsCache.length > 0 && (now - this.cacheTimestamp) < this.cacheTtl) {
      return this.agentsCache;
    }

    try {
      const response = await this.axiosInstance.get('/api/agent_builder/agents');
      this.agentsCache = response.data.agents || [];
      this.cacheTimestamp = now;
      return this.agentsCache;
    } catch (error: any) {
      console.error('Failed to get MCP server agents:', error);
      return [];
    }
  }

  async getAgent(agentId: string): Promise<Agent | null> {
    try {
      const response = await this.axiosInstance.get(`/api/agent_builder/agents/${agentId}`);
      return response.data;
    } catch (error: any) {
      console.error(`Failed to get MCP server agent ${agentId}:`, error);
      return null;
    }
  }

  async chat(
    inputText: string,
    conversationId?: string,
    agentId?: string,
    connectorId?: string
  ): Promise<ChatResponse> {
    // Prevent using "default" agent ID
    if (agentId === 'default') {
      agentId = undefined;
    }

    try {
      const payload: any = {
        input: inputText,
      };

      if (conversationId) {
        payload.conversation_id = conversationId;
      }

      if (agentId) {
        payload.agent_id = agentId;
      }

      if (connectorId) {
        payload.connector_id = connectorId;
      }

      const response = await this.axiosInstance.post('/api/agent_builder/mcp', payload);
      
      return {
        message: response.data.message || response.data.output || '',
        conversation_id: response.data.conversation_id || '',
        agent_id: response.data.agent_id || agentId,
        citations: response.data.citations || [],
      };
    } catch (error: any) {
      console.error('Failed to chat with MCP server:', error);
      throw new Error(`MCP Server API error: ${error.message}`);
    }
  }

  async getTools(): Promise<any[]> {
    const now = Date.now();
    if (this.toolsCache.length > 0 && (now - this.cacheTimestamp) < this.cacheTtl) {
      return this.toolsCache;
    }

    try {
      const response = await this.axiosInstance.get('/api/agent_builder/tools');
      this.toolsCache = response.data.tools || [];
      this.cacheTimestamp = now;
      return this.toolsCache;
    } catch (error: any) {
      console.error('Failed to get MCP server tools:', error);
      return [];
    }
  }

  async getConversations(): Promise<any[]> {
    try {
      const response = await this.axiosInstance.get('/api/agent_builder/conversations');
      return response.data.conversations || [];
    } catch (error: any) {
      console.error('Failed to get MCP server conversations:', error);
      return [];
    }
  }
}

// Singleton instance
let mcpService: MCPServerService | null = null;

export function getMCPServerService(): MCPServerService {
  if (!mcpService) {
    mcpService = new MCPServerService();
  }
  return mcpService;
}
