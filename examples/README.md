# LLM Integration Quick Start Guide

This directory contains practical examples and tools to help you set up LLM integration with your crop steering system.

## 📁 Files in this Directory

### `llm_config_examples.yaml`
Ready-to-copy configuration examples for different use cases:
- **Beginner Setup** ($1-2/day) - Perfect for learning and testing
- **Standard Setup** ($2-5/day) - Best for most home users
- **Premium Setup** ($5-10/day) - High-quality analysis for research
- **Testing Setup** ($0.50/day) - Emergency-only mode

## 🚀 Quick Setup (2 Minutes)

1. **Choose your budget** and copy the matching config from `llm_config_examples.yaml`
2. **Get an API key**:
   - OpenAI: https://platform.openai.com/api-keys
   - Claude: https://console.anthropic.com/
3. **Add to secrets.yaml**: `openai_api_key: "sk-your-key"`
4. **Test the setup** using Home Assistant service: `crop_steering.test_llm_api_key`
5. **Paste config** into `/config/appdaemon/apps/apps.yaml`
6. **Restart AppDaemon**

## 💰 Cost Examples (Real Usage)

| Setup Type | Model | Daily Cost | Monthly Cost | Best For |
|------------|--------|------------|--------------|----------|
| Beginner | GPT-4o Mini | $0.10-0.40 | $3-12 | Testing, learning |
| Standard | Claude Haiku | $0.20-0.80 | $6-24 | Daily automation |
| Premium | GPT-4o | $1.00-3.00 | $30-90 | Research, optimization |
| Emergency | GPT-4o Mini | $0.01-0.10 | $0.30-3 | Backup only |

*Costs shown include 70-90% caching reduction after first week*