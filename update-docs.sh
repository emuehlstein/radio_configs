#!/bin/bash
#
# Update all documentation locally
# This script regenerates all documentation files and can be run manually
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📚 OpenGD77 SSRFLite Generator - Documentation Update${NC}"
echo -e "${BLUE}=================================================${NC}"
echo

# Function to run documentation generator
run_generator() {
    local name="$1"
    local script="$2"
    local icon="$3"
    
    echo -e "${YELLOW}${icon} Generating $name documentation...${NC}"
    
    if uv run python "$script"; then
        echo -e "${GREEN}✅ $name documentation updated${NC}"
        echo
        return 0
    else
        echo -e "${RED}❌ Failed to generate $name documentation${NC}"
        echo
        return 1
    fi
}

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv is not installed. Please install uv first:${NC}"
    echo -e "${BLUE}   curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "generate_profile_docs.py" ]]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    exit 1
fi

# Generate all documentation
FAILED=false

run_generator "JSON Schema" "generate_ssrf_schema.py" "🧬" || FAILED=true
run_generator "Schema headers" "stamp_ssrf_headers.py" "🏷️" || FAILED=true
run_generator "Profile" "generate_profile_docs.py" "📋" || FAILED=true
run_generator "Policy" "generate_policy_docs.py" "⚙️" || FAILED=true  
run_generator "SSRF" "generate_ssrf_docs.py" "📡" || FAILED=true

# Summary
if [[ "$FAILED" == "true" ]]; then
    echo -e "${RED}❌ Some documentation generation failed${NC}"
    exit 1
else
    echo -e "${GREEN}🎉 All documentation updated successfully!${NC}"
    echo
    echo -e "${BLUE}📊 Documentation Summary:${NC}"
    
    # Count files
    PROFILE_COUNT=$(ls docs/profiles/*.md 2>/dev/null | grep -v README.md | wc -l || echo 0)
    POLICY_COUNT=$(ls docs/policies/*.md 2>/dev/null | grep -v README.md | wc -l || echo 0)
    SSRF_COUNT=$(ls docs/ssrf/*.md 2>/dev/null | grep -v README.md | wc -l || echo 0)
    
    echo -e "   📋 Profile docs: $PROFILE_COUNT files"
    echo -e "   ⚙️ Policy docs:  $POLICY_COUNT files"
    echo -e "   📡 SSRF docs:    $SSRF_COUNT files"
    echo
    
    echo -e "${BLUE}🔗 Browse documentation:${NC}"
    echo -e "   📋 Profiles: docs/profiles/README.md"
    echo -e "   ⚙️ Policies: docs/policies/README.md"
    echo -e "   📡 SSRF:     docs/ssrf/README.md"
fi