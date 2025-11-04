#!/bin/bash

echo "🔍 Checking AI HR Recruiter Project Files..."
echo ""

echo "📁 Project Root:"
ls -la "/Users/manav/CascadeProjects/ai hr recruiter/" | grep -v node_modules
echo ""

echo "📁 Backend Files:"
if [ -d "/Users/manav/CascadeProjects/ai hr recruiter/backend" ]; then
    ls -la "/Users/manav/CascadeProjects/ai hr recruiter/backend/"
else
    echo "❌ Backend folder not found"
fi
echo ""

echo "📁 Frontend Files:"
if [ -d "/Users/manav/CascadeProjects/ai hr recruiter/frontend/src" ]; then
    ls -la "/Users/manav/CascadeProjects/ai hr recruiter/frontend/src/"
else
    echo "❌ Frontend src folder not found (files were deleted)"
fi
echo ""

echo "✅ Files Created:"
echo "- backend/app.py"
echo "- backend/requirements.txt"
echo "- backend/.env.example"
echo "- README.md"
echo "- DEPLOY_GUIDE.md"
echo ""

echo "⚠️  Files Missing:"
echo "- All frontend source files (deleted)"
echo ""

echo "📋 What You Can Do:"
echo "1. Restore frontend from git: git checkout frontend/"
echo "2. Ask me to recreate all frontend files"
echo "3. Deploy backend only (Railway/Render/Heroku)"
echo ""
