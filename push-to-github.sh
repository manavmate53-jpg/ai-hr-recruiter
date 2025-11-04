#!/bin/bash

echo "🚀 Pushing AI HR Recruiter to GitHub..."
echo ""
echo "Repository: https://github.com/manavmate53-jpg/ai-hr-recruiter"
echo ""
echo "⚠️  You will be prompted for GitHub authentication:"
echo "   Username: manavmate53-jpg"
echo "   Password: Use your Personal Access Token (NOT your GitHub password)"
echo ""
echo "📝 Don't have a token? Get one here:"
echo "   https://github.com/settings/tokens/new"
echo "   - Select 'repo' scope"
echo "   - Copy the token and paste it when prompted"
echo ""
read -p "Press Enter to continue..."

git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "🔗 View your repo: https://github.com/manavmate53-jpg/ai-hr-recruiter"
    echo ""
    echo "📌 Next Steps:"
    echo "   1. Deploy to Netlify: https://app.netlify.com/"
    echo "   2. Or use GitHub Pages (see DEPLOY_TO_WEB.md)"
    echo "   3. Your app will be online 24/7 with a permanent link!"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "   1. Repository doesn't exist on GitHub - Create it at https://github.com/new"
    echo "   2. Authentication failed - Use Personal Access Token, not password"
    echo "   3. Network issues - Check your internet connection"
fi
