## Secure Tax Document Intelligence System
An AI-powered, memory-resident processing engine for sensitive tax documents.

This system is designed to allow tax professionals to upload, store, and process sensitive client documents securely while maintaining auditability and scalability.

## Current Features

- Zero-Disk Processing: Documents are handled as in-memory byte streams to ensure no sensitive data is written to local temp storage.
- AI-Powered Extraction: Integrated AWS Textract for high-accuracy OCR and Form extraction.
- Dual-Layer Auditing: Every action is logged to both a local forensic audit trail and a distributed Amazon DynamoDB table.
- Modular Backend Structure: Clean separation between ingestion, processing, and storage.

## Security

This system uses IAM policies to enforce least-privilege access.

- Restricted permissions to only allow file uploads and Textract analysis
- Scoped access to a specific S3 bucket
- In-Memory Lifecycle: Files are processed in RAM and uploaded to S3 without hitting the server file system.

## API File Validation
 
 This system enforces strict validation rules:

 - Only PDF files are accepted
 - Maximum file size limit: 5MB
 - Invalid files are rejected before processing

## System Flow

User --> FastAPI Ingestion --> AWS Textract --> AWS S3 --> Audit Logging

1. User provides a file via POST request
2. System converts file to memory-resident byte stream
3. Bytes are sent directly to AWS Textract for OCR and mapping
4. File is uploaded to AWS S3 via put_object
5. Metadata is logged to DynamoDB and local audit files

## Document Processing

Uploaded documents are processed to extract structured data using a hybrid AI and Regex approach.

Pipeline:
- Extract text and Form data via AWS Textract
- Classify document type (W2, 1099, Schedule C)
- Extract key fields (SSN, income)

Results are stored in structured JSON format for downstream tax workflows.

## Audit Logging (DynamoDB)

The system stores structured audit logs in DynamoDB for scalable tracking.

Each upload records:
- Timestamp (UTC)
- File name
- File size (calculated from byte stream)
- Upload method

## Storage Layer
This system uses Amazon S3 for secure, durable document storage.

Implementation:
- File uploads handled via Python (boto3)
- Objects stored directly from memory to S3 bucket
- Encrypted storage layer with scoped IAM access

## Roadmap

- Implement AWS KMS (Key Management Service) for S3 Envelope Encryption
- Add JWT-based authentication for tax professionals
- Build frontend dashboard for data verification
- Implement automated tax form validation rules

## Architecture Diagram

![Architecture](docs/architecture/architecture-v2.png)