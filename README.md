# s3_cleaner
## Overview
Current script provide possibillity to remove files from S3 buckets.
Files can be deleted by 2 conditions - part of file name and file age.

## Prerequisite
Dependencies should be installed.
```shell
pip install requiremets
```

## Usage
### List files
```shell
s3_clean.py list-objects --url https://<s3Storage> --id <s3Id> --key <s3Key> \
    --region <region> --bucket <bucketName>
```

### Delete files
```shell
s3_clean.py delete-objects --url https://<s3Storage> --id <s3Id> --key <s3Key> \
    --region <region> --bucket <bucketName> --namecontain <partOfFileName> --age <days>
```
