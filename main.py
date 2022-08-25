#!/usr/bin/env python3
import datetime
import syslog

import click
import boto3


s3_url = ''
s3_region = ''
s3_bucket = ''


@click.group()
def cli():
    pass


def connect(url, id, key, region):
    session = boto3.session.Session(aws_access_key_id=id, aws_secret_access_key=key, region_name=region)
    s3 = session.client(
        service_name='s3',
        endpoint_url=url,
        verify=False
    )
    return s3


def list_s3(bucket, s3):
    try:
        objects = s3.list_objects(Bucket=bucket)['Contents']
        return objects
    except KeyError as e:
        print(f"Error: bucket is empty")
        return []


def log_delete(response_code, object_name, bucket):
    if int(response_code) == 204:
        syslog.syslog(syslog.LOG_INFO, f"delete: {bucket}/{object_name} - {response_code}")
    else:
        syslog.syslog(syslog.LOG_CRIT, f"delete: {bucket}/{object_name} - {response_code}")


@cli.command(help="List S3 objects")
@click.option('--url', default=s3_url, help='S3 URL')
@click.option('--id', default="", help='S3 user id')
@click.option('--key', default="", help='S3 user secret key')
@click.option('--region', default=s3_region, help='S3 region')
@click.option('--bucket', default=s3_bucket, help='S3 bucket')
def list_objects(url, id, key, region, bucket):
    s3 = connect(url, id, key, region)
    for key in list_s3(bucket, s3):
        file_age = datetime.datetime.now(datetime.timezone.utc) - key['LastModified']
        print(f"Name: {key['Key']}\tSize: {key['Size']}\tModified days ago: {file_age.days}".expandtabs(50) )
    return key


@cli.command(help="Delete S3 objects")
@click.option('--url', default=s3_url, help='S3 URL')
@click.option('--id', default="", help='S3 user id')
@click.option('--key', default="", help='S3 user secret key')
@click.option('--region', default=s3_region, help='S3 region')
@click.option('--bucket', default=s3_bucket, help='S3 bucket')
@click.option('--all', is_flag=True, help='Delete all objects in bucket. Ignore other parameters')
@click.option('--namecontain', default="", help='Delete objects which name math string')
@click.option('--age', default="", help='Delete objects older than age days')
def delete_objects(url, id, key, region, bucket, all, namecontain, age):
    s3 = connect(url, id, key, region)
    code = {204: 'successfully deleted'}
    if all:
        for key in list_s3(bucket, s3):
            response = s3.delete_object(Bucket=bucket, Key=key['Key'])
            print(f"{key['Key']} - {code.get(response['ResponseMetadata']['HTTPStatusCode'],'Error')}")
            log_delete(response['ResponseMetadata']['HTTPStatusCode'], key['Key'], bucket)
    elif namecontain or age:
        objects_to_delete = []
        for key in s3.list_objects(Bucket=bucket)['Contents']:
            file_age = datetime.datetime.now(datetime.timezone.utc) - key['LastModified']
            if namecontain and namecontain not in key['Key']:
                continue
            if age and int(age) > int(file_age.days):
                continue
            else:
                objects_to_delete.append(key['Key'])
        if objects_to_delete:
            for key in objects_to_delete:
                response = s3.delete_object(Bucket=bucket, Key=key)
                print(f"{key} - {code.get(response['ResponseMetadata']['HTTPStatusCode'],'Error')}")
                log_delete(response['ResponseMetadata']['HTTPStatusCode'], key, bucket)
        else:
            print("Nothing to delete")
            syslog.syslog(syslog.LOG_INFO,
                          "s3_cleaner: nothing to delete")
    else:
        print("Nothing to do")
        syslog.syslog(syslog.LOG_INFO,
                      "s3_cleaner: no actions provided")


if __name__ == '__main__':
    cli()
