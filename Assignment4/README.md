# Azure End-to-End Data Pipeline — Superstore Dataset

Mini-project for the Data Analysis internship: build a Blob Storage → Azure Data Factory → Blob Storage pipeline with metadata validation, using the [Superstore dataset](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final) from Kaggle.

## Objective

Provision Azure infrastructure and build an ADF pipeline that:
1. Validates a source CSV file exists (via **Get Metadata**)
2. Copies it from a source container to a destination container (via **Copy Data**), gated on that validation succeeding
3. Is secured with IAM role assignments between ADF and Storage

## Architecture

```
Resource Group
 ├── Storage Account
 │    ├── Container: raw-data          (source, holds Superstore.csv)
 │    └── Container: processed-data    (destination)
 └── Azure Data Factory
      ├── Linked Service   → connects ADF to the Storage Account
      ├── Datasets         → DS_Superstore_Source, DS_Superstore_Sink
      └── Pipeline: PL_Superstore_EndToEnd
           GetFileMetadata (validates file) → CopySuperstoreData (copies file)

IAM: ADF's managed identity is granted "Storage Blob Data Contributor"
     on the Storage Account. A secondary account is granted "Reader"
     for view-only access, to demonstrate role scoping.
```

## Prerequisites

- Azure subscription (free tier is sufficient)
- Superstore dataset CSV downloaded from Kaggle
- Basic familiarity with the Azure Portal

## Setup Steps

### 1. Resource Group
Portal → **Resource groups** → **+ Create** → name `rg-superstore-pipeline`.

### 2. Storage Account + Containers
Portal → **Storage accounts** → **+ Create** → name e.g. `stsuperstoredemo` (Standard/LRS).
Create containers `raw-data` and `processed-data`. Upload `Superstore.csv` into `raw-data`.

### 3. Azure Data Factory
Portal → **Data factories** → **+ Create** (V2) → name e.g. `adf-superstore-demo` → **Launch Studio**.
Explore the three panes: **Author** (build), **Monitor** (track runs), **Manage** (linked services, IAM, triggers).

### 4. Linked Service
Manage → Linked services → New → Azure Blob Storage → authenticate via Account key, select your storage account.

### 5. Datasets
Author → Datasets → New → Azure Blob Storage → DelimitedText:
- `DS_Superstore_Source` → container `raw-data`, file `Superstore.csv`, first row as header
- `DS_Superstore_Sink` → container `processed-data`

### 6. Pipeline
Author → Pipelines → New → build (or import via **Code** view) the definition below.

```json
{
  "name": "PL_Superstore_EndToEnd",
  "properties": {
    "activities": [
      {
        "name": "GetFileMetadata",
        "type": "GetMetadata",
        "typeProperties": {
          "dataset": { "referenceName": "DS_Superstore_Source", "type": "DatasetReference" },
          "fieldList": ["itemName", "lastModified", "size", "exists"]
        }
      },
      {
        "name": "CopySuperstoreData",
        "type": "Copy",
        "dependsOn": [
          { "activity": "GetFileMetadata", "dependencyConditions": ["Succeeded"] }
        ],
        "typeProperties": {
          "source": { "type": "DelimitedTextSource", "storeSettings": { "type": "AzureBlobStorageReadSettings" } },
          "sink": { "type": "DelimitedTextSink", "storeSettings": { "type": "AzureBlobStorageWriteSettings" } }
        },
        "inputs": [{ "referenceName": "DS_Superstore_Source", "type": "DatasetReference" }],
        "outputs": [{ "referenceName": "DS_Superstore_Sink", "type": "DatasetReference" }]
      }
    ]
  }
}
```

### 7. Run and Monitor
- Click **Debug** on the pipeline canvas; confirm both activities show `Succeeded`.
- Check the **Monitor** tab for run status, duration, and start/end times.

### 8. IAM Roles
Storage Account → **Access control (IAM)** → **+ Add role assignment**:
- `Storage Blob Data Contributor` → ADF's managed identity (enables read/write on blobs)
- `Reader` → a secondary account or your own, at the resource group level (view-only, for comparison)

## Results

- Source file validated (existence, size, last-modified) before any copy occurred
- File successfully copied from `raw-data` to `processed-data`
- Pipeline run confirmed `Succeeded` in both Debug mode and Monitor
- Access between ADF and Storage scoped via IAM roles rather than embedded credentials

## Key Learnings

- **Linked Service vs Dataset**: a Linked Service is the connection to a data store; a Dataset is a named reference to a specific piece of data within it.
- **Activity dependency conditions** (`Succeeded` / `Failed` / `Completed`) let a pipeline branch or gate on the outcome of a prior activity — this is how metadata validation gates the copy.
- **Debug vs Trigger**: Debug runs are ad-hoc and used during development; Triggers (schedule, tumbling window, event-based) are for production.
- **IAM scoping**: Contributor grants read/write; Reader grants view-only — least-privilege access should match what a given identity actually needs to do.

## Repository / Deliverable Contents

| File | Description |
|---|---|
| `README.md` | This file — architecture and setup documentation |
| `pipeline/PL_Superstore_EndToEnd.json` | ADF pipeline definition |
| `screenshots/` | Portal screenshots evidencing each step (resource group, storage, ADF, pipeline run, IAM) |

## Dataset

[Superstore Sales Dataset — Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final)
