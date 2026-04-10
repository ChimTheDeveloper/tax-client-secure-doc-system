## Secure Tax Document Intelligence System
An AI-powered, memory-resident processing engine for sensitive tax documents.

This system is designed to allow tax professionals to upload, store, and process sensitive client documents securely while maintaining auditability, validation, and scalability.

---

## 🚀 Getting Started

# Prerequisites
- Python 3.11+
- AWS CLI configured with `us-east-1`
- Active S3 Bucket: `tax-doc-system-chim-dev`
- AWS IAM credentials with access to:
  - S3 (PutObject)
  - Textract (AnalyzeDocument)

---

# Installation
1. Clone the repository  
2. Create a virtual environment: `python3 -m venv venv`  
3. Activate: `source venv/bin/activate`  
4. Install dependencies: `pip install -r requirements.txt`  

---

# Running the Application

Because the application uses a modular structure, always run the server from the **root directory**:

# Set the Python Path so internal modules are discoverable
export PYTHONPATH=$PYTHONPATH:.

# Start the FastAPI server
uvicorn src.api.main:app --reload

---

## Current Features

- Zero-Disk Processing: Documents are handled as in-memory byte streams to ensure no sensitive data is written to local storage.
- AI-Powered Extraction: Integrated with Amazon Textract for OCR and structured form extraction.
- Document Classification: Automatically identifies document types (W-2 supported).
- Multi-Pass Extraction Engine:
  - KEY_VALUE extraction (primary)
  - LINE-based fallback
  - Regex-based precision extraction
- Structured W-2 Mapping: Extracts SSN, EIN, wages, and tax fields.
- Validation Layer: Rejects low-confidence or incomplete results (HTTP 422).
- Normalization Layer: Converts extracted values into clean, usable formats.
- Audit Logging (Local): Logs file activity, size, and timestamps in `audit_log.txt`.
- Modular Backend Structure: Clear separation between ingestion, processing, and storage.

---

## Security

This system uses IAM policies to enforce least-privilege access.

- Restricted permissions to only allow file uploads and Textract analysis  
- Scoped access to a specific S3 bucket  
- In-Memory Lifecycle: Files are processed in RAM and uploaded to S3 without hitting the server file system  

---

## API File Validation
 
This system enforces strict validation rules:

- Only PDF files are accepted  
- Maximum file size limit: 5MB  
- Empty or invalid files are rejected before processing  

---

## System Flow

User --> FastAPI Ingestion --> AWS Textract --> Processing Pipeline --> AWS S3 --> Audit Logging

1. User provides a file via POST request  
2. System converts file to memory-resident byte stream  
3. Bytes are sent directly to Amazon Textract for OCR and form analysis  
4. Document is classified (W-2 detection)  
5. Multi-pass extraction is applied (KEY_VALUE → LINE → REGEX)  
6. Extracted data is validated  
7. Data is normalized into structured format  
8. File is uploaded to AWS S3 via boto3  
9. Metadata is logged locally  

---

## Document Processing

Uploaded documents are processed using a hybrid AI and rule-based system.

Pipeline:
- Extract text and form data via Amazon Textract  
- Classify document type (W-2 currently supported)  
- Extract key fields (SSN, EIN, wages, tax fields)  
- Apply multi-pass extraction for reliability  
- Validate extracted data  
- Normalize values into usable formats  

Results are stored in structured JSON format for downstream tax workflows.

---

## Audit Logging

The system maintains a local audit log for traceability.

Each upload records:
- Timestamp (UTC)  
- File name  
- File size (calculated from byte stream)  
- Processing status  

Note: DynamoDB logging is planned but currently disabled.

---

## Storage Layer

This system uses Amazon S3 for secure, durable document storage.

Implementation:
- File uploads handled via Python (boto3)  
- Objects stored directly from memory to S3 bucket  
- No local disk persistence  
- IAM-restricted access  

---

## Current Limitations

- Address extraction is heuristic-based (not layout-aware yet)  
- Confidence scoring uses categorical labels (not numeric yet)  
- DynamoDB persistence is temporarily disabled  
- Only W-2 fully supported  

---

## Roadmap

- Implement AWS KMS (Key Management Service) for S3 encryption  
- Add JWT-based authentication for tax professionals  
- Reintroduce DynamoDB with structured schema  
- Build frontend dashboard for data verification  
- Implement numeric confidence scoring (0–1 scale)  
- Add human review flag for low-confidence outputs  
- Expand support for additional tax forms (1099, Schedule C)  
- Introduce cost tracking and FinOps optimization  

---

## Positioning

This project demonstrates:

- Cloud-native backend engineering  
- Serverless architecture design  
- AI-assisted document processing  
- Data validation and normalization pipelines  
- Secure handling of sensitive financial data

## Architecture Diagram

![Architecture](docs/architecture/architecture-v2.png)