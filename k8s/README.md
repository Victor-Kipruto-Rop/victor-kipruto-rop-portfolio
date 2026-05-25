# ☸️ Kubernetes Orchestration Layer

This directory contains the production-grade orchestration manifests for the banking and telecom data platform.

## 🏗️ Architecture
The platform is designed to run on a Kubernetes cluster, providing high availability and automated scaling for both the database and visualization layers.

## 📁 Structure
- `/absa`: Manifests for the Absa Integrated Analytics platform.
- `/kcb`: Manifests for KCB Financial Performance tracking.
- `/kra`: Manifests for National Revenue & Trade intelligence.

## 🚀 Usage
To deploy the platform to a cluster:
```bash
kubectl create namespace data-pipelines
kubectl apply -f k8s/absa/absa-platform.yaml
```

## Data Sources
This orchestration layer manages projects that utilize:
- Audited Financial Reports (2021-2025)
- KRA Customs & Revenue Datasets
- Safaricom Operational Disclosures
