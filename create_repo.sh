#!/bin/bash

# This script will create the GitHub repository
# You'll need a GitHub Personal Access Token

echo "=== GitHub Repository Creation Script ==="
echo ""
echo "Repository Name: agentic-ai-investment-research-assistant"
echo "Description: Production-ready agentic AI system for investment research and portfolio analytics"
echo ""
echo "This script requires a GitHub Personal Access Token with 'repo' scope."
echo ""
echo "To create a token:"
echo "1. Go to https://github.com/settings/tokens"
echo "2. Click 'Generate new token (classic)'"
echo "3. Select 'repo' scope"
echo "4. Copy the token"
echo ""
read -p "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
echo ""

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: No token provided"
    exit 1
fi

echo "Creating repository..."

# Create the repository
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "agentic-ai-investment-research-assistant",
    "description": "Production-ready agentic AI system for investment research and portfolio analytics. Features self-directed planning, dynamic tool selection, comprehensive guardrails, and observability.",
    "private": false,
    "has_issues": true,
    "has_projects": true,
    "has_wiki": false
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 201 ]; then
    echo "✅ Repository created successfully!"
    echo ""
    echo "Adding remote and pushing code..."
    
    # Add remote
    git remote add origin https://github.com/sanathpabba/agentic-ai-investment-research-assistant.git
    
    # Push code
    git push -u origin main
    
    echo ""
    echo "✅ Code pushed successfully!"
    echo ""
    echo "Repository URL: https://github.com/sanathpabba/agentic-ai-investment-research-assistant"
    echo ""
    echo "Next steps:"
    echo "1. Add topics to your repository"
    echo "2. Update LinkedIn project with repository link"
    echo "3. Share your project!"
else
    echo "❌ Error creating repository (HTTP $HTTP_CODE)"
    echo "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"
    exit 1
fi
