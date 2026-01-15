# AI Agent Prompts Guide

## 📚 Available Prompt Versions

This folder contains different versions of AI Agent prompts optimized for different use cases.

---

## 🎯 Which Version to Use?

### **Simple Version** (Recommended for most cases)
📄 **Files**: `ai_agent_prompts_simple_pt.md` | `ai_agent_prompts_simple_en.md`

**Best for:**
- ✅ Quick implementation
- ✅ Clear and direct tool usage
- ✅ Focus on the 8 Unity Catalog functions
- ✅ Practical examples with real outputs
- ✅ Less verbose, more actionable

**Structure:**
- Tools with clear "when to use" guidance
- Simple workflows (3-4 steps)
- Practical examples with complete responses
- Metrics interpretation guide
- Direct SQL examples

**Use when:**
- Implementing a new AI Agent
- Need quick reference
- Want concise prompts
- Prefer practical examples over theory

---

### **Complete Version** (Comprehensive)
📄 **Files**: `ai_agent_prompts_pt.md` | `ai_agent_prompts_en.md`

**Best for:**
- ✅ Comprehensive documentation
- ✅ 25+ common questions examples
- ✅ Detailed domain knowledge
- ✅ Multiple use case templates
- ✅ Configuration examples

**Structure:**
- Extended catalog of 25+ common questions
- Domain knowledge section
- Response templates
- Ad-hoc question examples
- Python configuration samples

**Use when:**
- Need comprehensive reference
- Training new team members
- Building complex AI workflows
- Want extensive examples

---

## 📊 Version Comparison

| Feature | Simple Version | Complete Version |
|---------|----------------|------------------|
| **Length** | ~300 lines | ~360 lines |
| **Tools Section** | Focused (8 tools with usage) | Brief list |
| **Examples** | 3 detailed with outputs | SQL snippets only |
| **Workflows** | Step-by-step (3-4 steps) | Multiple scenarios |
| **Common Questions** | Embedded in examples | 25+ dedicated section |
| **Metrics Guide** | ✅ Included | ✅ Included |
| **Response Format** | ✅ With example | ✅ Template only |
| **Best for** | Quick start, implementation | Reference, training |

---

## 🗂️ File Structure

```
prompts/
├── ai_agent_prompts_simple_pt.md    # 🎯 Simple - Portuguese
├── ai_agent_prompts_simple_en.md    # 🎯 Simple - English
├── ai_agent_prompts_pt.md           # 📖 Complete - Portuguese  
├── ai_agent_prompts_en.md           # 📖 Complete - English
├── genie_example_prompts_pt.md      # Databricks Genie prompts
├── genie_example_prompts_en.md      # Databricks Genie prompts
└── README_PROMPTS.md                # This file
```

---

## 🚀 Quick Start

### For Databricks AI Agent:

1. **Choose your version:**
   - Fast implementation? → Use **Simple version**
   - Need full reference? → Use **Complete version**

2. **Select language:**
   - Portuguese: `*_pt.md`
   - English: `*_en.md`

3. **Copy the System Prompt:**
   - Open the chosen file
   - Copy the content inside the first markdown block
   - Paste into your Databricks AI Agent configuration

4. **Test with example questions:**
   - Simple version: See "Exemplos Práticos" section
   - Complete version: See "Common Questions" section

---

## 🛠️ Unity Catalog Functions Reference

All prompts use these 8 functions:

| Function | Parameter | Returns |
|----------|-----------|---------|
| `get_company_id_by_name` | company_name | Company search results |
| `get_ticket_by_id` | ticket_id | Complete ticket info |
| `get_ticket_interactions` | ticket_id | Conversation history |
| `get_ticket_full_conversation` | ticket_id | Ticket + array (for AI) |
| `get_company_info` | company_id | Complete company data |
| `get_company_tickets_summary` | company_id | Ticket statistics |
| `get_customer_info` | customer_id | Customer profile |
| `get_agent_info` | agent_id | Agent performance |

📝 **Note**: All functions require only ONE parameter (an ID or name)

---

## 💡 Tips

### Simple Version Tips:
- Start here if it's your first AI Agent
- Focus on the 8 tools and workflows
- Use the practical examples as templates
- Metrics interpretation is built-in

### Complete Version Tips:
- Use as comprehensive documentation
- Great for training materials
- Reference the 25+ common questions
- Python configuration included

---

## 🔄 Migration Between Versions

### From Complete to Simple:
Already implemented the complete version? No changes needed!
The simple version uses the same tools with:
- More concise explanations
- Practical examples with outputs
- Streamlined workflows

### From Simple to Complete:
Want more examples?
- Keep using the same 8 functions
- Add more use cases from complete version
- Incorporate 25+ common questions

---

## 📞 Support

For questions about:
- **Unity Catalog Functions**: See `sql/unity_catalog_functions.sql`
- **Function Usage**: See either prompt version
- **Implementation**: Start with Simple version
- **Advanced Use Cases**: See Complete version

---

**Last Updated**: 2026-01-15  
**Versions**: Simple v1.0, Complete v1.0
