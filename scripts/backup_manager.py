import os
import boto3
import logging
from datetime import datetime, timedelta
import subprocess
import hashlib
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self):
        self.s3_client = boto3.client('s3')
        self.bucket_name = os.getenv('BACKUP_BUCKET_NAME', 'hr-analytics-backups')
        self.backup_dir = Path('/backups')
        self.retention_days = {
            'daily': 7,
            'weekly': 30,
            'monthly': 365
        }
        
    def create_backup(self):
        """Create a new database backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = self.backup_dir / f'backup_{timestamp}.dump'
            
            # Create backup
            cmd = [
                'pg_dump',
                '-U', 'postgres',
                '-d', 'app',
                '-F', 'c',
                '-f', str(backup_file)
            ]
            
            logger.info(f"Creating backup: {backup_file}")
            subprocess.run(cmd, check=True)
            
            # Calculate checksum
            checksum = self._calculate_checksum(backup_file)
            
            # Upload to S3
            self._upload_to_s3(backup_file, checksum)
            
            # Clean up local file
            backup_file.unlink()
            
            logger.info(f"Backup completed successfully: {backup_file.name}")
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            return False
            
    def _calculate_checksum(self, file_path):
        """Calculate SHA-256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
        
    def _upload_to_s3(self, file_path, checksum):
        """Upload file to S3 with metadata"""
        try:
            metadata = {
                'checksum': checksum,
                'backup_type': self._determine_backup_type(),
                'timestamp': datetime.now().isoformat()
            }
            
            self.s3_client.upload_file(
                str(file_path),
                self.bucket_name,
                file_path.name,
                ExtraArgs={
                    'Metadata': metadata,
                    'ServerSideEncryption': 'AES256'
                }
            )
            
            logger.info(f"Uploaded to S3: {file_path.name}")
            
        except Exception as e:
            logger.error(f"S3 upload failed: {str(e)}")
            raise
            
    def _determine_backup_type(self):
        """Determine if this is a daily, weekly, or monthly backup"""
        now = datetime.now()
        if now.day == 1:
            return 'monthly'
        elif now.weekday() == 0:  # Monday
            return 'weekly'
        return 'daily'
        
    def rotate_backups(self):
        """Rotate backups based on retention policy"""
        try:
            # List all backups in S3
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name
            )
            
            if 'Contents' not in response:
                return
                
            for obj in response['Contents']:
                metadata = self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=obj['Key']
                )['Metadata']
                
                backup_type = metadata.get('backup_type', 'daily')
                retention_days = self.retention_days[backup_type]
                
                last_modified = obj['LastModified']
                age = (datetime.now(last_modified.tzinfo) - last_modified).days
                
                if age > retention_days:
                    logger.info(f"Deleting old backup: {obj['Key']} (age: {age} days)")
                    self.s3_client.delete_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    
        except Exception as e:
            logger.error(f"Backup rotation failed: {str(e)}")
            
    def verify_backups(self):
        """Verify the integrity of recent backups"""
        try:
            # Get the most recent backup
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1
            )
            
            if 'Contents' not in response:
                logger.warning("No backups found to verify")
                return
                
            latest_backup = response['Contents'][0]
            metadata = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=latest_backup['Key']
            )['Metadata']
            
            # Download and verify checksum
            local_path = self.backup_dir / latest_backup['Key']
            self.s3_client.download_file(
                self.bucket_name,
                latest_backup['Key'],
                str(local_path)
            )
            
            calculated_checksum = self._calculate_checksum(local_path)
            stored_checksum = metadata.get('checksum')
            
            if calculated_checksum == stored_checksum:
                logger.info(f"Backup verification successful: {latest_backup['Key']}")
            else:
                logger.error(f"Backup verification failed: {latest_backup['Key']}")
                
            # Clean up
            local_path.unlink()
            
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            
    def restore_backup(self, backup_key):
        """Restore a specific backup"""
        try:
            # Download backup
            local_path = self.backup_dir / backup_key
            self.s3_client.download_file(
                self.bucket_name,
                backup_key,
                str(local_path)
            )
            
            # Verify checksum
            metadata = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=backup_key
            )['Metadata']
            
            calculated_checksum = self._calculate_checksum(local_path)
            if calculated_checksum != metadata.get('checksum'):
                raise ValueError("Backup integrity check failed")
                
            # Restore database
            cmd = [
                'pg_restore',
                '-U', 'postgres',
                '-d', 'app',
                '-F', 'c',
                str(local_path)
            ]
            
            logger.info(f"Restoring backup: {backup_key}")
            subprocess.run(cmd, check=True)
            
            # Clean up
            local_path.unlink()
            
            logger.info(f"Backup restored successfully: {backup_key}")
            return True
            
        except Exception as e:
            logger.error(f"Backup restore failed: {str(e)}")
            return False

def main():
    manager = BackupManager()
    
    # Create new backup
    if manager.create_backup():
        # Rotate old backups
        manager.rotate_backups()
        
        # Verify recent backups
        manager.verify_backups()

if __name__ == "__main__":
    main() 