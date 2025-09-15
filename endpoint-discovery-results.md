# 1Chat API Endpoint Discovery Results

## Summary
Successfully discovered new endpoints after enabling the `agentBuilder:enabled` setting in Kibana. The test script has been updated with comprehensive endpoint testing capabilities and now uses environment variables for configuration.

## 🔧 Configuration
The script now reads configuration from environment variables:
- **`ELASTICSEARCH_URL`** - Automatically converted from Elasticsearch URL to Kibana URL
- **`ELASTICSEARCH_API_KEY`** - API key for authentication
- **Automatic URL conversion** - Converts `.es.` URLs to `.kb.` URLs for Kibana API access

### Environment Setup
The script uses the `dotenv` package to load environment variables from a `.env` file:
```bash
# Install dotenv dependency
npm install dotenv

# .env file example
ELASTICSEARCH_URL=https://ai-assistants-ffcafb.es.us-east-1.aws.elastic.cloud:443
ELASTICSEARCH_API_KEY=your_api_key_here
```

### Security
- The `.env` file is properly ignored in `.gitignore` to prevent committing sensitive information
- The script provides fallback values for development/testing purposes
- Configuration validation shows which values are being used

## ✅ Working Endpoints Discovered

### Agent Builder Endpoints
- **`/api/agent_builder/agents` (GET)** - Lists available agents
  - Returns 5 agents including "elastic-ai-agent" and "cisco-nextgen"
  - Each agent has: id, type, name, description, configuration
  - Configuration includes tools with tool_ids arrays

- **`/api/agent_builder/tools` (GET)** - Lists available tools
  - Returns 11 tools including "platform.core.search" and others
  - Each tool has: id, type, description, tags, configuration, readonly, schema
  - Tools have detailed descriptions and schemas

### POST Endpoints (Partial Success)
- **`/api/agent_builder/agents` (POST)** - Creates new agents
  - Requires "id" field in request body
  - Returns 400 error with specific validation messages
  - Suggests working endpoint for agent creation

- **`/api/agent_builder/tools` (POST)** - Creates new tools
  - Requires "id" field and specific "type" values ("esql" or "index_search")
  - Returns 400 error with validation details
  - Suggests working endpoint for tool creation

### System Endpoints
- **`/api/features` (GET)** - Lists available features
- **`/api/status` (GET)** - System status information
- **`/app/elasticsearch/api/chat/tools` (GET)** - Alternative chat tools path
- **`/app/elasticsearch/api/agent_builder` (GET)** - Alternative agent builder path

## 🔍 Authentication Details
- **ApiKey authentication** works for all discovered endpoints
- **Bearer/Basic auth** returns 401 (requires different format)
- **kbn-xsrf header** is required for all requests
- **Content-Type: application/json** is required

## 📊 Data Structure Examples

### Agent Structure
```json
{
  "id": "elastic-ai-agent",
  "type": "chat",
  "name": "Elastic AI Agent",
  "description": "Elastic AI Agent",
  "configuration": {
    "tools": [{
      "tool_ids": [
        "platform.core.search",
        "platform.core.list_indices",
        "platform.core.get_index_mapping",
        "platform.core.get_document_by_id"
      ]
    }]
  }
}
```

### Tool Structure
```json
{
  "id": "platform.core.search",
  "type": "builtin",
  "description": "A powerful tool for searching and analyzing data...",
  "tags": [],
  "configuration": {},
  "readonly": true,
  "schema": {}
}
```

## ❌ Endpoints Not Found
- No `/internal/` endpoints working with current authentication
- No 1Chat specific endpoints found
- No models or configs endpoints found
- No `/create` or `/new` suffix endpoints found
- No working chat conversation endpoints found

## 🔧 Updated Test Script Features
The `deep-chat-test.js` script has been enhanced with:
- Comprehensive endpoint discovery for agent builder APIs
- Multiple authentication method testing
- Detailed response analysis
- POST endpoint testing with proper request bodies
- Summary generation with findings
- Error handling and validation message parsing

## 🎯 Key Findings
1. **Agent Builder is functional** - The enabled setting has activated agent builder APIs
2. **RESTful API design** - Endpoints follow standard REST patterns
3. **Validation is strict** - POST endpoints require specific field formats
4. **Authentication is consistent** - ApiKey works across all discovered endpoints
5. **Rich data available** - Both agents and tools have detailed metadata

## 📝 Recommendations
1. Use the discovered endpoints to integrate with your existing 1Chat system
2. Implement proper request body validation for POST operations
3. Consider using the agent builder APIs to create custom agents for your use case
4. Test the POST endpoints with proper field validation to create new resources
5. Monitor for additional endpoints that may become available with future updates

## 🔄 Next Steps
1. Test creating agents and tools using the discovered POST endpoints
2. Explore the available tools to understand their capabilities
3. Integrate the agent builder APIs into your application
4. Monitor for new endpoints as the feature continues to evolve
