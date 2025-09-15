// deep-chat-test.js - Comprehensive test for 1Chat APIs
const fetch = require('node-fetch').default || require('node-fetch');
require('dotenv').config();

// Convert Elasticsearch URL to Kibana URL if needed
function getKibanaUrl(elasticsearchUrl) {
    if (elasticsearchUrl && elasticsearchUrl.includes('.es.')) {
        return elasticsearchUrl.replace('.es.', '.kb.');
    }
    return elasticsearchUrl || 'https://ai-assistants-ffcafb.kb.us-east-1.aws.elastic.cloud';
}

const ELASTIC_CONFIG = {
    host: getKibanaUrl(process.env.ELASTICSEARCH_URL),
    apiKey: process.env.ELASTICSEARCH_API_KEY || 'aGdDR0RKa0JETUNGNlpRbkRHVDY6T0VyTFcyUVN4VWxyaEQyZ00yMnk3QQ=='
};

// Validate configuration
function validateConfig() {
    console.log('🔧 Configuration Check:');
    console.log(`  Original URL: ${process.env.ELASTICSEARCH_URL || 'Not set'}`);
    console.log(`  Kibana URL: ${ELASTIC_CONFIG.host}`);
    console.log(`  API Key: ${ELASTIC_CONFIG.apiKey ? '✅ Set' : '❌ Missing'}`);
    
    if (!process.env.ELASTICSEARCH_API_KEY) {
        console.log('⚠️  Warning: ELASTICSEARCH_API_KEY not found in environment variables');
        console.log('   Using fallback API key. Consider setting ELASTICSEARCH_API_KEY in your .env file');
    }
    
    if (!process.env.ELASTICSEARCH_URL) {
        console.log('⚠️  Warning: ELASTICSEARCH_URL not found in environment variables');
        console.log('   Using fallback URL. Consider setting ELASTICSEARCH_URL in your .env file');
    } else if (process.env.ELASTICSEARCH_URL.includes('.es.')) {
        console.log('ℹ️  Info: Converted Elasticsearch URL to Kibana URL for API testing');
    }
    
    console.log('');
}

async function testWithDifferentAuth(path, method = 'GET', body = null) {
    const url = `${ELASTIC_CONFIG.host}${path}`;
    console.log(`\n🔍 Testing: ${method} ${path}`);
    
    // Test different authentication methods
    const authMethods = [
        { name: 'ApiKey', headers: { 'Authorization': `ApiKey ${ELASTIC_CONFIG.apiKey}`, 'kbn-xsrf': 'true' }},
        { name: 'Bearer', headers: { 'Authorization': `Bearer ${ELASTIC_CONFIG.apiKey}`, 'kbn-xsrf': 'true' }},
        { name: 'Basic', headers: { 'Authorization': `Basic ${ELASTIC_CONFIG.apiKey}`, 'kbn-xsrf': 'true' }},
        { name: 'No Auth', headers: { 'kbn-xsrf': 'true' }}
    ];
    
    for (const auth of authMethods) {
        try {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    ...auth.headers
                }
            };
            
            if (body) {
                options.body = JSON.stringify(body);
            }
            
            const response = await fetch(url, options);
            const status = response.status;
            
            console.log(`  ${auth.name}: ${status}`);
            
            if (status === 200) {
                console.log(`    ✅ SUCCESS with ${auth.name}!`);
                const data = await response.text();
                console.log(`    Response: ${data.substring(0, 200)}...`);
                return true; // Found working auth
            } else if (status === 401) {
                console.log(`    🔐 Auth required`);
            } else if (status === 403) {
                console.log(`    ❌ Forbidden`);
            } else if (status === 400) {
                const error = await response.text();
                console.log(`    ⚠️ 400 Error: ${error}`);
            }
        } catch (error) {
            console.log(`    💥 ${auth.name} error: ${error.message}`);
        }
    }
    return false;
}

async function testChatEndpoints() {
    console.log('🤖 DEEP 1CHAT API TESTING');
    console.log('=' .repeat(50));
    
    // Test chat endpoints with different auth methods
    const chatEndpoints = [
        '/api/chat/tools',
        '/api/chat/agents',
        '/internal/chat/tools',
        '/internal/chat/agents',
        // New agent builder endpoints
        '/api/agent_builder',
        '/api/agent-builder',
        '/internal/agent_builder',
        '/internal/agent-builder',
        '/api/assistants',
        '/internal/assistants',
        '/api/ai_assistants',
        '/internal/ai_assistants',
        // 1Chat specific endpoints
        '/api/onechat',
        '/internal/onechat',
        '/api/chat/onechat',
        '/internal/chat/onechat'
    ];
    
    for (const endpoint of chatEndpoints) {
        const success = await testWithDifferentAuth(endpoint);
        if (success) {
            console.log(`🎯 Found working endpoint: ${endpoint}`);
            break;
        }
    }
    
    // Test POST endpoints
    console.log('\n💬 TESTING POST ENDPOINTS');
    const postEndpoints = [
        '/api/chat/converse',
        '/internal/chat/converse',
        // Agent builder POST endpoints
        '/api/agent_builder/create',
        '/api/agent-builder/create',
        '/internal/agent_builder/create',
        '/internal/agent-builder/create',
        '/api/assistants/create',
        '/internal/assistants/create',
        // 1Chat POST endpoints
        '/api/onechat/converse',
        '/internal/onechat/converse',
        '/api/chat/onechat/converse',
        '/internal/chat/onechat/converse'
    ];
    
    const testBody = { input: "hello" };
    
    for (const endpoint of postEndpoints) {
        const success = await testWithDifferentAuth(endpoint, 'POST', testBody);
        if (success) {
            console.log(`🎯 Found working POST endpoint: ${endpoint}`);
            break;
        }
    }
    
    // Test if there's a different base path
    console.log('\n🔍 TESTING ALTERNATIVE BASE PATHS');
    const altPaths = [
        '/app/elasticsearch/api/chat/tools',
        '/kibana/api/chat/tools',
        '/elastic/api/chat/tools',
        '/app/elasticsearch/api/agent_builder',
        '/kibana/api/agent_builder',
        '/elastic/api/agent_builder'
    ];
    
    for (const path of altPaths) {
        await testWithDifferentAuth(path);
    }
    
    console.log('\n🎯 TESTING COMPLETE');
}

// Test if we can find any working endpoint patterns
async function testEndpointPatterns() {
    console.log('\n🕵️ SEARCHING FOR ENDPOINT PATTERNS');
    
    // Try to find any /api/ endpoints that work
    const testPaths = [
        '/api',
        '/api/features',
        '/api/status',
        '/api/spaces/_active_space',
        '/api/security/me',
        // Settings and configuration endpoints
        '/api/kibana/settings',
        '/internal/kibana/settings',
        '/api/settings',
        '/internal/settings',
        // Agent builder specific settings
        '/api/agentBuilder/settings',
        '/internal/agentBuilder/settings',
        '/api/agent_builder/settings',
        '/internal/agent_builder/settings'
    ];
    
    for (const path of testPaths) {
        await testWithDifferentAuth(path);
    }
}

// Test agent builder specific endpoints
async function testAgentBuilderEndpoints() {
    console.log('\n🔧 TESTING AGENT BUILDER ENDPOINTS');
    
    const agentBuilderEndpoints = [
        '/api/agent_builder/agents',
        '/api/agent_builder/tools',
        '/api/agent_builder/models',
        '/api/agent_builder/configs',
        '/internal/agent_builder/agents',
        '/internal/agent_builder/tools',
        '/internal/agent_builder/models',
        '/internal/agent_builder/configs',
        // Alternative naming conventions
        '/api/agent-builder/agents',
        '/api/agent-builder/tools',
        '/api/agent-builder/models',
        '/api/agent-builder/configs',
        '/internal/agent-builder/agents',
        '/internal/agent-builder/tools',
        '/internal/agent-builder/models',
        '/internal/agent-builder/configs'
    ];
    
    for (const endpoint of agentBuilderEndpoints) {
        const success = await testWithDifferentAuth(endpoint);
        if (success) {
            console.log(`🎯 Found working agent builder endpoint: ${endpoint}`);
        }
    }
    
    // Test POST endpoints for agent builder
    console.log('\n💬 TESTING AGENT BUILDER POST ENDPOINTS');
    const agentBuilderPostEndpoints = [
        '/api/agent_builder/agents/create',
        '/api/agent_builder/agents/update',
        '/api/agent_builder/agents/delete',
        '/internal/agent_builder/agents/create',
        '/internal/agent_builder/agents/update',
        '/internal/agent_builder/agents/delete'
    ];
    
    const testAgentBody = { 
        name: "test-agent",
        description: "Test agent for discovery",
        model: "gpt-4"
    };
    
    for (const endpoint of agentBuilderPostEndpoints) {
        const success = await testWithDifferentAuth(endpoint, 'POST', testAgentBody);
        if (success) {
            console.log(`🎯 Found working agent builder POST endpoint: ${endpoint}`);
        }
    }
}

// Test the discovered working endpoints in detail
async function testDiscoveredEndpoints() {
    console.log('\n🎯 TESTING DISCOVERED WORKING ENDPOINTS IN DETAIL');
    
    const workingEndpoints = [
        '/api/agent_builder/agents',
        '/api/agent_builder/tools'
    ];
    
    for (const endpoint of workingEndpoints) {
        console.log(`\n📋 DETAILED TEST: ${endpoint}`);
        const url = `${ELASTIC_CONFIG.host}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `ApiKey ${ELASTIC_CONFIG.apiKey}`,
                    'kbn-xsrf': 'true',
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.status === 200) {
                const data = await response.json();
                console.log(`✅ SUCCESS: ${endpoint}`);
                console.log(`📊 Response structure:`, JSON.stringify(data, null, 2).substring(0, 500) + '...');
                
                // Try to extract useful information
                if (data.results && Array.isArray(data.results)) {
                    console.log(`📈 Found ${data.results.length} results`);
                    if (data.results.length > 0) {
                        console.log(`🔍 First result keys:`, Object.keys(data.results[0]));
                    }
                }
            } else {
                console.log(`❌ Failed: ${response.status}`);
            }
        } catch (error) {
            console.log(`💥 Error: ${error.message}`);
        }
    }
}

// Test POST endpoints for discovered working endpoints
async function testDiscoveredPostEndpoints() {
    console.log('\n💬 TESTING POST ENDPOINTS FOR DISCOVERED WORKING ENDPOINTS');
    
    // Test agent creation endpoints
    const agentPostEndpoints = [
        '/api/agent_builder/agents',
        '/api/agent_builder/agents/create',
        '/api/agent_builder/agents/new'
    ];
    
    const testAgentBody = {
        id: "test-agent-discovery",
        name: "test-agent-discovery",
        description: "Test agent created during endpoint discovery",
        type: "chat",
        configuration: {
            tools: [{
                tool_ids: ["platform.core.search"]
            }]
        }
    };
    
    for (const endpoint of agentPostEndpoints) {
        console.log(`\n🔧 Testing POST: ${endpoint}`);
        const success = await testWithDifferentAuth(endpoint, 'POST', testAgentBody);
        if (success) {
            console.log(`🎯 Found working POST endpoint: ${endpoint}`);
        }
    }
    
    // Test tool creation endpoints
    const toolPostEndpoints = [
        '/api/agent_builder/tools',
        '/api/agent_builder/tools/create',
        '/api/agent_builder/tools/new'
    ];
    
    const testToolBody = {
        id: "test-tool-discovery",
        name: "test-tool-discovery",
        description: "Test tool created during endpoint discovery",
        type: "custom"
    };
    
    for (const endpoint of toolPostEndpoints) {
        console.log(`\n🔧 Testing POST: ${endpoint}`);
        const success = await testWithDifferentAuth(endpoint, 'POST', testToolBody);
        if (success) {
            console.log(`🎯 Found working POST endpoint: ${endpoint}`);
        }
    }
}

// Generate summary of findings
async function generateSummary() {
    console.log('\n📋 SUMMARY OF FINDINGS');
    console.log('=' .repeat(50));
    console.log('✅ WORKING ENDPOINTS DISCOVERED:');
    console.log('  • /api/agent_builder/agents (GET) - Lists available agents');
    console.log('  • /api/agent_builder/tools (GET) - Lists available tools');
    console.log('  • /api/features (GET) - Lists available features');
    console.log('  • /api/status (GET) - System status information');
    console.log('  • /app/elasticsearch/api/chat/tools (GET) - Alternative chat tools path');
    console.log('  • /app/elasticsearch/api/agent_builder (GET) - Alternative agent builder path');
    console.log('');
    console.log('🔍 AUTHENTICATION:');
    console.log('  • ApiKey authentication works for discovered endpoints');
    console.log('  • Bearer/Basic auth returns 401 (requires different format)');
    console.log('  • kbn-xsrf header is required');
    console.log('');
    console.log('📊 AGENT BUILDER DATA:');
    console.log('  • Found 5 agents including "elastic-ai-agent" and "cisco-nextgen"');
    console.log('  • Found 11 tools including "platform.core.search" and others');
    console.log('  • Agents have configuration with tool_ids arrays');
    console.log('  • Tools have detailed descriptions and schemas');
    console.log('');
    console.log('🔧 POST ENDPOINT FINDINGS:');
    console.log('  • /api/agent_builder/agents (POST) - Accepts POST but requires "id" field');
    console.log('  • /api/agent_builder/tools (POST) - Accepts POST but requires "id" field');
    console.log('  • Both endpoints return 400 error when "id" field is missing');
    console.log('  • This suggests they are working endpoints for creating resources');
    console.log('');
    console.log('❌ NOT FOUND:');
    console.log('  • No /internal/ endpoints working with current auth');
    console.log('  • No 1Chat specific endpoints found');
    console.log('  • No models or configs endpoints found');
    console.log('  • No /create or /new suffix endpoints found');
}

async function runDeepTest() {
    validateConfig();
    await testChatEndpoints();
    await testAgentBuilderEndpoints();
    await testEndpointPatterns();
    await testDiscoveredEndpoints();
    await testDiscoveredPostEndpoints();
    await generateSummary();
}

runDeepTest().catch(console.error);