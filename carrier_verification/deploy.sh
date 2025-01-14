#!/bin/bash

echo "Starting deployment process..."

# Remove old package directory if it exists
echo "Cleaning up old deployment files..."
rm -rf deployment/package
rm -rf deployment/venv

# Create new package directory
echo "Creating new package directory..."
mkdir -p deployment/package

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv deployment/venv
source deployment/venv/bin/activate

# Install packages with platform specification for Lambda
echo "Installing dependencies..."
pip install --platform manylinux2014_x86_64 --target ./deployment/package --implementation cp --python-version 3.10 --only-binary=:all: --upgrade -r requirements.txt

# Copy application code
echo "Copying application code..."
cp -r app ./deployment/package/

# Create ZIP file
echo "Creating deployment ZIP file..."
cd deployment/package
zip -r ../lambda_function.zip .
cd ../..

# Cleanup
deactivate
rm -rf deployment/venv

echo "Deployment package created: deployment/lambda_function.zip"
echo "Deploy completed successfully!"