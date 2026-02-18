---
name: file-processing
description: Stream processing, large file uploads, and IO efficiency.
role: eng-backend
triggers:
  - upload
  - csv import
  - excel
  - stream
  - large file
  - s3 upload
---

# file-processing Skill

This skill guides the handling of binary data and large datasets without blowing up RAM.

## 1. Streaming (Chunks)
- **Problem**: Reading 1GB CSV into memory (RAM).
- **Solution**: Stream it line by line.
  - nodejs: `fs.createReadStream().pipe(csvParser())`.
  - python: `pd.read_csv(chunksize=1000)`.

## 2. Uploads (Presigned URLs)
- **Anti-Pattern**: Client -> Server (RAM buffer) -> S3.
- **Pattern**: Client -> (Request URL) -> Server; Server -> (Signed URL) -> Client; Client -> (Direct Upload) -> S3.
- **Benefit**: Server CPU/RAM is zero during upload. Infinite scalability.

## 3. Malware Scanning
- Never trust user files.
- **Sync**: ClamAV scan on upload (slow).
- **Async**: Upload to S3 (Quarantine Bucket) -> Lambda triggers Scan -> Move to Clean Bucket.

## 4. Exporting Large Data
- Don't return 100k rows in JSON response (timeout).
- **Pattern**:
  1. User requests Export.
  2. Server puts job in Queue.
  3. Worker generates CSV, uploads to S3.
  4. Server notifies User with Download Link.

## 5. File Types
- **Magic Bytes**: Check file signature (hex), not just extension.
- **Image Processing**: Resize/Optimize *async*. Use `sharp` (Node) or `Pillow` (Python).
