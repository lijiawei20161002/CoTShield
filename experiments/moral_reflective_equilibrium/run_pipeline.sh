#!/bin/bash
#
# Quick pipeline runner for moral reflective equilibrium experiment
# Usage: ./run_pipeline.sh [all|data|finetune|eval]
#

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python environment
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: python3 not found${NC}"
    exit 1
fi

# Check API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}Warning: OPENAI_API_KEY not set${NC}"
    echo "Please set it with: export OPENAI_API_KEY='your-key'"
    exit 1
fi

# Create directories
mkdir -p data results

# Parse command
COMMAND=${1:-all}

run_step() {
    echo -e "\n${GREEN}==== $1 ====${NC}\n"
    python3 "$2"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1 completed${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
}

if [ "$COMMAND" == "all" ] || [ "$COMMAND" == "data" ]; then
    echo -e "${GREEN}Running data generation pipeline...${NC}"

    run_step "Step 1: Generate scenarios" "scripts/1_generate_scenarios.py"
    run_step "Step 2: Collect preferences" "scripts/2_collect_preferences.py"
    run_step "Step 3: Detect inconsistencies" "scripts/3_detect_inconsistencies.py"
    run_step "Step 4: Generate reflections" "scripts/4_generate_reflections.py"
    run_step "Step 5: Prepare finetuning data" "scripts/5_prepare_finetuning.py"

    echo -e "\n${GREEN}Data generation complete!${NC}"
    echo -e "Next step: Run finetuning with ${YELLOW}./run_pipeline.sh finetune${NC}"
fi

if [ "$COMMAND" == "all" ] || [ "$COMMAND" == "finetune" ]; then
    echo -e "${GREEN}Starting finetuning...${NC}"

    if [ ! -f "data/finetuning_train.jsonl" ]; then
        echo -e "${RED}Error: Training data not found. Run './run_pipeline.sh data' first${NC}"
        exit 1
    fi

    run_step "Step 6: Run finetuning" "scripts/6_run_finetuning.py"

    echo -e "\n${GREEN}Finetuning started!${NC}"
    echo -e "Monitor with: ${YELLOW}python scripts/monitor_finetuning.py${NC}"
fi

if [ "$COMMAND" == "eval" ]; then
    echo -e "${GREEN}Running evaluation...${NC}"

    if [ -z "$2" ]; then
        echo -e "${RED}Error: Finetuned model ID required${NC}"
        echo "Usage: ./run_pipeline.sh eval <finetuned-model-id>"
        exit 1
    fi

    FINETUNED_MODEL="$2"

    echo -e "\n${GREEN}Evaluating baseline model...${NC}"
    python3 scripts/7_evaluate.py --model gpt-4-turbo-preview --eval-type original

    echo -e "\n${GREEN}Evaluating finetuned model...${NC}"
    python3 scripts/7_evaluate.py --model "$FINETUNED_MODEL" --eval-type original

    echo -e "\n${GREEN}Analyzing results...${NC}"
    python3 scripts/8_analyze_results.py \
        --baseline eval_original_gpt-4-turbo-preview.json \
        --finetuned "eval_original_${FINETUNED_MODEL//:/_}.json" \
        --output-prefix final_analysis

    echo -e "\n${GREEN}Evaluation complete!${NC}"
    echo -e "Results saved in ${YELLOW}results/${NC}"
fi

if [ "$COMMAND" != "all" ] && [ "$COMMAND" != "data" ] && [ "$COMMAND" != "finetune" ] && [ "$COMMAND" != "eval" ]; then
    echo "Usage: ./run_pipeline.sh [all|data|finetune|eval]"
    echo ""
    echo "Commands:"
    echo "  all       - Run full pipeline (data + finetune)"
    echo "  data      - Run data generation only (steps 1-5)"
    echo "  finetune  - Run finetuning (step 6)"
    echo "  eval      - Run evaluation and analysis (steps 7-8)"
    echo "              Usage: ./run_pipeline.sh eval <finetuned-model-id>"
    exit 1
fi
