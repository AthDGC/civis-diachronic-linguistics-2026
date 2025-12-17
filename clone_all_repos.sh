#!/bin/bash

# ============================================================================
# CLONE ALL GITHUB REPOSITORIES - Professor Nikolaos Lavidas
# Repository List from: https://github.com/nlavidas?tab=repositories
# Date: December 10, 2024
# ============================================================================

echo "=========================================="
echo "Cloning All GitHub Repositories"
echo "User: nlavidas"
echo "Target: /root/linguistics-workspace/github-repos/"
echo "=========================================="

# Create workspace structure
cd /root
mkdir -p linguistics-workspace/{github-repos,new-materials,corpus-data,scripts-standalone,documentation}
cd linguistics-workspace/github-repos

echo ""
echo "📁 Current directory: $(pwd)"
echo ""

# ============================================================================
# CATEGORY 1: MAIN PROJECTS & PLATFORMS
# ============================================================================

echo "📦 Cloning Main Projects..."

git clone git@github.com:nlavidas/AthDGC-Diagloss.git
git clone git@github.com:nlavidas/AthDGC-online-github-io.git
git clone git@github.com:nlavidas/AthDGC-project-pre-final-2024.git
git clone git@github.com:nlavidas/AI-cline-corpus-project.git
git clone git@github.com:nlavidas/diachrony-working-2025.git
git clone git@github.com:nlavidas/diachrony-working-platform-mds-tei-md2.git
git clone git@github.com:nlavidas/test-working-online-env-2-december2024.git

# ============================================================================
# CATEGORY 2: CHATBOTS & AI ASSISTANTS
# ============================================================================

echo "🤖 Cloning Chatbots & AI Projects..."

git clone git@github.com:nlavidas/chatbot-diachrony-ai.git
git clone git@github.com:nlavidas/chatbot-philology-ai.git
git clone git@github.com:nlavidas/chatbot-try-log-2024.git
git clone git@github.com:nlavidas/lavidas-new-better-eduvacy-Chatbot-22.git
git clone git@github.com:nlavidas/ChatbotProject.git

# ============================================================================
# CATEGORY 3: COURSES & TEACHING MATERIALS
# ============================================================================

echo "📚 Cloning Course Materials..."

git clone git@github.com:nlavidas/ADE52-courses-github-io.git
git clone git@github.com:nlavidas/pms-lavidas-class.git
git clone git@github.com:nlavidas/WinterSchool-Clitics.git

# ============================================================================
# CATEGORY 4: DATASETS & CORPORA
# ============================================================================

echo "📊 Cloning Datasets & Corpora..."

git clone git@github.com:nlavidas/diachrony-corpus.git
git clone git@github.com:nlavidas/datasets-for-english-greek.git
git clone git@github.com:nlavidas/datasets-lavidas-razi-greek-pr.git
git clone git@github.com:nlavidas/PROIEL-Datasets-Byzantine-GRC.git

# ============================================================================
# CATEGORY 5: DASHBOARDS & VISUALIZATIONS
# ============================================================================

echo "📈 Cloning Dashboards..."

git clone git@github.com:nlavidas/lavidas-razi-dashboard.git

# ============================================================================
# CATEGORY 6: DOCUMENTATION & RESEARCH
# ============================================================================

echo "📝 Cloning Documentation..."

git clone git@github.com:nlavidas/GreekRetrDB.git
git clone git@github.com:nlavidas/lavidas-razi-tree-bank-2025.git

# ============================================================================
# CATEGORY 7: COLLECTION & INDEX REPOS
# ============================================================================

echo "🗂️ Cloning Collections..."

git clone git@github.com:nlavidas/lavidas-collection.git
git clone git@github.com:nlavidas/lavidas-repo-collector.git

# ============================================================================
# CATEGORY 8: EXPERIMENTAL & WORKING REPOS
# ============================================================================

echo "🔬 Cloning Experimental Projects..."

git clone git@github.com:nlavidas/gamified06.git
git clone git@github.com:nlavidas/lavidas-try-log-2024.git
git clone git@github.com:nlavidas/lavidasN3.git
git clone git@github.com:nlavidas/nlavidas.git

# ============================================================================
# CATEGORY 9: TECHNICAL TOOLS & UTILITIES
# ============================================================================

echo "🔧 Cloning Tools..."

git clone git@github.com:nlavidas/node-v-SYNTAX-TREE_NLAE.git
git clone git@github.com:nlavidas/LdEv.git

# ============================================================================
# CATEGORY 10: GITHUB PAGES & WEBSITES
# ============================================================================

echo "🌐 Cloning Websites..."

git clone git@github.com:nlavidas/nlavidas.github.io.git

# ============================================================================
# POST-CLONE SUMMARY
# ============================================================================

echo ""
echo "=========================================="
echo "✅ CLONING COMPLETE!"
echo "=========================================="
echo ""
echo "📊 Repository Summary:"
echo "Total repositories cloned: $(ls -1 | wc -l)"
echo ""
echo "📁 Repository Categories:"
echo "   - Main Projects: 7 repos"
echo "   - Chatbots & AI: 5 repos"
echo "   - Courses: 3 repos"
echo "   - Datasets: 4 repos"
echo "   - Dashboards: 1 repo"
echo "   - Documentation: 2 repos"
echo "   - Collections: 2 repos"
echo "   - Experimental: 4 repos"
echo "   - Tools: 2 repos"
echo "   - Websites: 1 repo"
echo ""
echo "📂 Location: /root/linguistics-workspace/github-repos/"
echo ""
echo "🔍 To view all repos:"
echo "   cd /root/linguistics-workspace/github-repos"
echo "   ls -la"
echo ""
echo "=========================================="

# Optional: Create a repository inventory
cd /root/linguistics-workspace
cat > REPOS_INVENTORY.txt << 'EOF'
# GitHub Repository Inventory - Professor Nikolaos Lavidas
# Generated: December 10, 2024
# Total: 31 repositories

## MAIN PROJECTS & PLATFORMS (7)
1. AthDGC-Diagloss
2. AthDGC-online-github-io
3. AthDGC-project-pre-final-2024
4. AI-cline-corpus-project
5. diachrony-working-2025
6. diachrony-working-platform-mds-tei-md2
7. test-working-online-env-2-december2024

## CHATBOTS & AI ASSISTANTS (5)
8. chatbot-diachrony-ai
9. chatbot-philology-ai
10. chatbot-try-log-2024
11. lavidas-new-better-eduvacy-Chatbot-22
12. ChatbotProject

## COURSES & TEACHING MATERIALS (3)
13. ADE52-courses-github-io
14. pms-lavidas-class
15. WinterSchool-Clitics

## DATASETS & CORPORA (4)
16. diachrony-corpus
17. datasets-for-english-greek
18. datasets-lavidas-razi-greek-pr
19. PROIEL-Datasets-Byzantine-GRC

## DASHBOARDS (1)
20. lavidas-razi-dashboard

## DOCUMENTATION & RESEARCH (2)
21. GreekRetrDB
22. lavidas-razi-tree-bank-2025

## COLLECTIONS (2)
23. lavidas-collection
24. lavidas-repo-collector

## EXPERIMENTAL (4)
25. gamified06
26. lavidas-try-log-2024
27. lavidasN3
28. nlavidas

## TOOLS (2)
29. node-v-SYNTAX-TREE_NLAE
30. LdEv

## WEBSITES (1)
31. nlavidas.github.io

EOF

echo "📄 Created: REPOS_INVENTORY.txt"
echo ""
echo "Next steps:"
echo "1. Review any clone errors above"
echo "2. Upload new materials from Z: drive to /root/linguistics-workspace/new-materials/"
echo "3. Run Cline's Master Onboarding prompt"
echo ""
