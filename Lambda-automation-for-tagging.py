import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Get all instances
    instances = ec2.describe_instances()['Reservations']
    
    for reservation in instances:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_name = None
            
            # Get the Name tag of the instance
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
            
            if instance_name:
                for volume in instance['BlockDeviceMappings']:
                    volume_id = volume['Ebs']['VolumeId']
                    
                    # Get the volume creation date
                    volume_info = ec2.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]
                    creation_date = volume_info['CreateTime'].strftime('%Y')
                    volume_name = f"volume_{instance_name}_{creation_date}"
                    
                    # Tagging the volume
                    ec2.create_tags(Resources=[volume_id], Tags=[
                        {'Key': 'Name', 'Value': volume_name}
                    ])
                    
                    # Find snapshots for this volume
                    snapshots = ec2.describe_snapshots(Filters=[{'Name': 'volume-id', 'Values': [volume_id]}], OwnerIds=['self'])['Snapshots']
                    for snapshot in snapshots:
                        snapshot_id = snapshot['SnapshotId']
                        snapshot_creation_date = snapshot['StartTime'].strftime('%Y')
                        snapshot_name = f"volume_snapshot_{instance_name}_{snapshot_creation_date}"
                        
                        # Tagging the snapshot
                        ec2.create_tags(Resources=[snapshot_id], Tags=[
                            {'Key': 'Name', 'Value': snapshot_name}
                        ])
                    
                    # Get all AMIs
                    images = ec2.describe_images(Owners=['self'])['Images']
    
                    for image in images:
                        image_id = image['ImageId']
                        creation_date = image['CreationDate'][:4]
                        ami_name = f"AMI_{instance_name}_{creation_date}"
            
                        # Tagging the AMI
                        ec2.create_tags(Resources=[image_id], Tags=[
                            {'Key': 'Name', 'Value': ami_name}
                        ])
    
    return {
        'statusCode': 200,
        'body': 'Tagging completed successfully'
    }
