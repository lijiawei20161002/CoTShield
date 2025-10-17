#!/bin/bash
# CoTShield Test Runner
# Runs all unit and integration tests

set -e

echo "========================================="
echo "CoTShield Test Suite"
echo "========================================="
echo ""

# Run detector tests
echo "Running detector tests..."
python -m unittest tests.test_detector -v

echo ""
echo "Running reconstructor tests..."
python -m unittest tests.test_reconstructor -v

echo ""
echo "Running viewer API tests..."
python -m unittest tests.test_viewer -v

echo ""
echo "========================================="
echo "All tests passed!"
echo "========================================="
