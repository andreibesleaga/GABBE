---
name: file-processing
description: "Handle large files and uploads without exhausting memory: streaming, presigned uploads, malware scanning, background exports, file-type checks. Use when code reads or writes big files, accepts user uploads or exports large datasets."
triggers: [file processing, large file upload, stream a large file, presigned url upload, csv export, malware scan upload]
tags: [coding]
role: eng-backend
context_cost: low
---
# file-processing Skill

## Goal
This skill guides the handling of binary data and large datasets without blowing up RAM.

## Steps
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

## Constraints
- Process data as a stream with bounded memory: do not collect chunks in an array before handling them.
- Check the file type by its signature (magic bytes), not by extension.
- Never trust a user file: scan it before it is served.

## Output Format
Code for the file pipeline, plus a short note on chunk size, size limits, where files are stored and how they are scanned.

## Limits and safety
- Archives: cap total size, decompression ratio and entry count, and reject any entry whose path leaves the target directory.
- Presigned upload URLs: one object key, PUT only, expiry of 15 minutes or less.
- The application must not serve an uploaded file before the scan has finished and the file has moved out of quarantine.
- Rate-limit and deduplicate export and upload jobs, with a quota per user.
- Inspect untrusted files with maintained libraries in an isolated worker, not in the main application process.
