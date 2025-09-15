#!/usr/bin/env python3
"""
Script to create a specialized Snort agent for Elastic 1Chat
This agent will be configured to work with Snort alert data
"""

import requests
import json
import sys
from config import get_settings

def create_snort_agent():
    """Create a specialized Snort agent for 1Chat"""
    
    settings = get_settings()
    
    # 1Chat API configuration
    base_url = settings.elasticsearch_url
    api_key = settings.elasticsearch_api_key
    
    headers = {
        'Authorization': f'ApiKey {api_key}',
        'Content-Type': 'application/json',
        'kbn-xsrf': 'true'
    }
    
    # Snort agent configuration
    agent_data = {
        "id": "snort_security_agent",
        "name": "Snort Security Analyst",
        "description": "A specialized AI agent for analyzing Snort security alerts and providing expert recommendations",
        "configuration": {
            "instructions": """You are a senior cybersecurity analyst specializing in Snort intrusion detection system (IDS) alerts. Your expertise includes:

1. **Alert Analysis**: Analyze Snort alerts to identify potential security threats, false positives, and attack patterns
2. **Risk Assessment**: Evaluate the severity and potential impact of detected threats
3. **Incident Response**: Provide actionable recommendations for responding to security incidents
4. **Network Security**: Understand network protocols, attack vectors, and defensive measures
5. **Threat Intelligence**: Correlate alerts with known attack patterns and threat actors

When analyzing alerts, always consider:
- Alert priority and classification
- Source and destination IP addresses
- Protocol and port information
- Timestamp and frequency of alerts
- Potential attack patterns or sequences

Provide clear, actionable recommendations that security teams can implement immediately. Use technical language appropriate for cybersecurity professionals but explain complex concepts when necessary.

Focus on:
- Immediate response actions
- Long-term security improvements
- False positive identification
- Threat hunting opportunities
- Compliance considerations""",
            "tools": [
                {
                    "tool_ids": [".search"]
                }
            ]
        }
    }
    
    try:
        # Create the agent
        response = requests.post(
            f"{base_url}/api/chat/agents",
            headers=headers,
            json=agent_data
        )
        
        if response.status_code == 200:
            print("✅ Successfully created Snort Security Agent!")
            print(f"Agent ID: {agent_data['id']}")
            print(f"Agent Name: {agent_data['name']}")
            print(f"Description: {agent_data['description']}")
            return True
        else:
            print(f"❌ Failed to create agent. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return False

def test_agent():
    """Test the created agent with a sample question"""
    
    settings = get_settings()
    
    base_url = settings.elasticsearch_url
    api_key = settings.elasticsearch_api_key
    
    headers = {
        'Authorization': f'ApiKey {api_key}',
        'Content-Type': 'application/json',
        'kbn-xsrf': 'true'
    }
    
    # Test message
    test_data = {
        "input": "I'm seeing multiple high-priority Snort alerts from the same source IP. What should I do?",
        "agent_id": "snort_security_agent"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/chat/converse",
            headers=headers,
            json=test_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("\n🧪 Testing the Snort agent...")
            print(f"✅ Agent responded successfully!")
            print(f"Response: {result.get('message', 'No message')[:200]}...")
            return True
        else:
            print(f"❌ Test failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating Snort Security Agent for 1Chat...")
    print("=" * 50)
    
    if create_snort_agent():
        print("\n" + "=" * 50)
        test_agent()
    else:
        print("❌ Failed to create agent. Exiting.")
        sys.exit(1)
