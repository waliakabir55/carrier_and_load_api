#!/bin/bash

echo "Starting deployment process..."

# Remove old directories
rm -rf deployment/package
rm -rf deployment/venv

# Create directories
mkdir -p deployment/package

# Create virtual environment
python -m venv deployment/venv
source deployment/venv/bin/activate

# Install dependencies
pip install --platform manylinux2014_x86_64 --target ./deployment/package --implementation cp --python-version 3.10 --only-binary=:all: -r requirements.txt

# Copy application code
cp -r app/* deployment/package/

# Create ZIP
cd deployment/package
zip -r ../lambda_function.zip .
cd ../..

# Cleanup
deactivate
rm -rf deployment/venv

echo "Deployment package created: deployment/lambda_function.zip"