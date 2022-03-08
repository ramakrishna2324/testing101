#!/usr/bin/python
import boto3
from pprint import pprint
import argparse
import time
#from utility import add_ec2_tag


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--account_number", help="account number")
    parser.add_argument("-rn", "--role_name", help="role")
    parser.add_argument("-r", "--region", help="region", default="us-east-1")

    parser.add_argument("-s", "--image_description", help="image_description")
    parser.add_argument("-sg", "--instance_id", help="instance_id")
    parser.add_argument("-k", "--image_name", help="image_name")

    return parser.parse_args()


def aws_assume_role(account_number, role_arn):
    sts_client = boto3.client('sts')

    role_arn = "arn:aws:iam::" + str(account_number) + ":role/" + role_arn

    assumedRoleObject = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="AssumeRole")

    return assumedRoleObject['Credentials']


def add_tags(ec2_client, resource_id, name):
    response = ec2_client.create_tags(
        Resources=[
            resource_id,
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': name
            },
            {
                'Key': 'component',
                'Value': 'jdfdevopsci'
            }
        ]
    )
    pprint(response)


def make_client(credentials, region, service):
    return boto3.client(
        service,
        region_name=region,
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken']
    )


if __name__ == '__main__':
    args = parse_arguments()
    credentials = aws_assume_role(args.account_number, args.role_name)
    ec2_client = make_client(credentials, args.region, "ec2")

    response = ec2_client.create_image(
        Description=args.image_description,
        InstanceId=args.instance_id,
        Name=args.image_name
    )
    pprint(response)
    image_id = response["ImageId"]
    #output required for Jenkinsfile
    print "image_id: " + image_id

    image_status = ""
    while image_status != "available":
        res = ec2_client.describe_images(ImageIds=[image_id, ])
        image_status = res['Images'][0]['State']
        print("Checking status of AMI ID %s : %s" %(image_id, image_status))
        time.sleep(5)

    add_tags(ec2_client, image_id, args.image_name)
