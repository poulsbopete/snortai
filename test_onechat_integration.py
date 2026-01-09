#!/usr/bin/env python3
"""
Test script for Elastic MCP server integration
Demonstrates the complete functionality of the MCP server service
"""

import sys
import os
sys.path.append('/opt/snortai')

from app.services.onechat import onechat_service

def test_onechat_integration():
    """Test all MCP server functionality"""
    
    print("🚀 Testing Elastic MCP Server Integration")
    print("=" * 60)
    
    # Test 1: Get available agents
    print("\n1️⃣ Testing Agent Discovery")
    print("-" * 30)
    try:
        agents = onechat_service.get_agents()
        print(f"✅ Found {len(agents)} agents:")
        for agent in agents:
            print(f"   • {agent.id}: {agent.name}")
            if agent.id == 'snortai':
                print(f"     Description: {agent.description[:100]}...")
    except Exception as e:
        print(f"❌ Failed to get agents: {e}")
        return False
    
    # Test 2: Get available tools
    print("\n2️⃣ Testing Tool Discovery")
    print("-" * 30)
    try:
        tools = onechat_service.get_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools[:5]:  # Show first 5 tools
            print(f"   • {tool.get('id', 'unknown')}: {tool.get('description', 'no description')[:60]}...")
    except Exception as e:
        print(f"❌ Failed to get tools: {e}")
        return False
    
    # Test 3: Chat with Snort AI agent
    print("\n3️⃣ Testing Snort AI Agent Chat")
    print("-" * 30)
    try:
        response = onechat_service.chat(
            input_text="What are the most common types of alerts in my Snort system?",
            agent_id="snortai"
        )
        print(f"✅ Chat successful!")
        print(f"   Conversation ID: {response.conversation_id}")
        print(f"   Response length: {len(response.message)} characters")
        print(f"   Response preview:")
        print(f"   {response.message[:200]}...")
        print(f"   Citations: {len(response.citations or [])} sources")
    except Exception as e:
        print(f"❌ Chat failed: {e}")
        return False
    
    # Test 4: Continue conversation
    print("\n4️⃣ Testing Conversation Continuity")
    print("-" * 30)
    try:
        follow_up_response = onechat_service.chat(
            input_text="Can you show me alerts from the last hour?",
            conversation_id=response.conversation_id,
            agent_id="snortai"
        )
        print(f"✅ Follow-up chat successful!")
        print(f"   Same conversation ID: {follow_up_response.conversation_id == response.conversation_id}")
        print(f"   Response length: {len(follow_up_response.message)} characters")
        print(f"   Response preview:")
        print(f"   {follow_up_response.message[:200]}...")
    except Exception as e:
        print(f"❌ Follow-up chat failed: {e}")
        return False
    
    # Test 5: Get conversation history
    print("\n5️⃣ Testing Conversation History")
    print("-" * 30)
    try:
        conversations = onechat_service.get_conversations()
        print(f"✅ Found {len(conversations)} total conversations")
        if conversations:
            latest_conv = conversations[0]
            print(f"   Latest conversation: {latest_conv.get('id', 'unknown')}")
            print(f"   Last activity: {latest_conv.get('last_activity', 'unknown')}")
    except Exception as e:
        print(f"❌ Failed to get conversations: {e}")
        return False
    
    # Test 6: Chat without specifying agent (uses system default)
    print("\n6️⃣ Testing Chat Without Agent ID")
    print("-" * 30)
    try:
        # Don't specify agent_id - let the system use its default
        default_response = onechat_service.chat(
            input_text="Hello, can you help me understand what the MCP server can do?"
            # No agent_id specified - will use system default
        )
        print(f"✅ Chat without agent ID successful!")
        print(f"   Response length: {len(default_response.message)} characters")
        print(f"   Response preview:")
        print(f"   {default_response.message[:200]}...")
    except Exception as e:
        print(f"❌ Chat without agent ID failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! MCP server integration is working perfectly!")
    print("=" * 60)
    
    return True

def demo_snort_analysis():
    """Demonstrate Snort-specific analysis capabilities"""
    
    print("\n🔍 Snort Analysis Demo")
    print("=" * 40)
    
    # Demo queries for Snort analysis
    demo_queries = [
        "Show me high priority alerts from the last 24 hours",
        "What are the most active source IPs in my alerts?",
        "Are there any port scanning activities detected?",
        "Show me HTTP-related alerts and their details",
        "What patterns do you see in the alert data?"
    ]
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 50)
        try:
            response = onechat_service.chat(
                input_text=query,
                agent_id="snortai"
            )
            print(f"✅ Response ({len(response.message)} chars):")
            print(f"{response.message[:300]}...")
            if len(response.message) > 300:
                print("   [Response truncated for demo]")
        except Exception as e:
            print(f"❌ Query failed: {e}")

if __name__ == "__main__":
    print("Starting MCP Server Integration Tests...")
    
    # Run basic integration tests
    if test_onechat_integration():
        # Run Snort-specific demo
        demo_snort_analysis()
    else:
        print("❌ Basic integration tests failed. Please check your configuration.")
        sys.exit(1)
