name: Build and Deploy to SAP AI Core

on:
  push:
    branches: [ "main" ]
    paths:
      - 'sap-deployment/**'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4

    - name: Build Docker Image
      uses: docker/build-push-action@v4
      with:
        context: ./sap-deployment
        push: true
        tags: ghcr.io/${{ github.repository }}:latest

    - name: Deploy to SAP AI Core
      env:
        SAP_CLIENT_ID: ${{ secrets.SAP_CLIENT_ID }}
        SAP_CLIENT_SECRET: ${{ secrets.SAP_CLIENT_SECRET }}
        SAP_SERVICE_KEY: ${{ secrets.SAP_SERVICE_KEY }}
      run: |
        pip install sap-ai-core-sdk
        echo "$SAP_SERVICE_KEY" > service_key.json
        sapcli login --client-id "$SAP_CLIENT_ID" --client-secret "$SAP_CLIENT_SECRET"
        sapcli deployment create -f sap-deployment/serving.yaml