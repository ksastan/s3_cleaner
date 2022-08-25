# s3_cleaner
## Overview
Current script provide possibillity to remove files from S3 buckets.
Files can be deleted by 2 conditions - part of file name and file age.

## Usage
### List files
```
s3_clean.py list-objects --url https://<s3Storage> --id <s3Id> --key <s3Key> --region <region> --bucket <bucketName>
```

