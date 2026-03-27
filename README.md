## Secure Tax Document Processing System
A secure, serverless tax document processing system built on AWS

This system is designed to allow tax professionals to upload, store, and process sensitive client documents securely while maintaining auditibility and scalability.

## Current Features

- File upload system built in Python
- Integration with AWS S3 for cloud storage
- Audit logging system for tracking uploads
- Input validation for file handling
- Modular backend structure

## Security

This system uses IAM policies to enforce least-privilege access.

- Restricted permissions to only allow file uploads
- Scoped access to a specific S3 bucket

This ensures secure interaction with cloud resources.

## API File Validation
 
 This system enforces strict validation rules:

 - Only PDF files are accepted
 - Maximum file size limit: 5MB
 - Invalid files are rejected before processing

 These controls ensure safe and predictable document ingestion.

## System Flow

User --> Upload Script --> AWS S3 --> Audit Logging

1. User provides a file
2. System validates file existence
3. File is uploaded to AWS S3
4. Metadata is logged for audit tracking

## Audit Logging

Each uploaded file generates a log entry containing:

- Timestamp
- File name
- File size
- Destination (S3 bucket)

This provides traceability and lays the foundation for compliance and monitoring.

## Storage Layer
This system uses Amazon S3 for secure document storage.

Implementation:
- File uploads handled via Python (boto3)
- Objects stored in S3 bucket
- Scaleable and durable storage layer

## Roadmap

- Implement IAM role-based access control
- Restrict S3 permissions
- Add database layer (DynamoDB) for structured logging
- Build document processing pipeline (AWS Lambda)
- Add authentication system

## Architecture Diagram

![Architecture](docs/architecture/architecture-v1.png)