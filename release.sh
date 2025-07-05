#!/usr/bin/env bash

# Script to build and publish modern-django-starter to PyPI
# Usage: ./release.sh [test|prod]

set -e

# Determine environment
ENV=${1:-test}

echo "🚀 Building modern-django-starter package..."

# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build

# Check the package
echo "🔍 Checking package..."
twine check dist/*

if [ "$ENV" = "test" ]; then
    echo "📦 Uploading to Test PyPI..."
    twine upload --repository testpypi dist/*
    echo "✅ Upload complete! Test with:"
    echo "pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ modern-django-starter"
elif [ "$ENV" = "prod" ]; then
    echo "📦 Uploading to Production PyPI..."
    twine upload dist/*
    echo "✅ Upload complete! Install with:"
    echo "pip install modern-django-starter"
else
    echo "❌ Invalid environment. Use 'test' or 'prod'"
    exit 1
fi
