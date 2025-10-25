"""
AWS Credentials Setup Helper

This script helps configure AWS credentials for the Farmer Budget Optimizer.
"""

import os
import sys
from pathlib import Path


def setup_aws_credentials():
    """Interactive AWS credentials setup."""
    print("🔧 AWS Credentials Setup for Farmer Budget Optimizer")
    print("=" * 55)
    
    print("\nThis script will help you configure AWS credentials.")
    print("You can choose from several options:")
    print("\n1. Use AWS CLI configuration (recommended)")
    print("2. Set environment variables")
    print("3. Use temporary test credentials")
    print("4. Skip AWS setup (use mock data only)")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            setup_aws_cli()
            break
        elif choice == "2":
            setup_environment_variables()
            break
        elif choice == "3":
            setup_test_credentials()
            break
        elif choice == "4":
            print("\n✅ Skipping AWS setup. The system will use mock data.")
            print("You can configure AWS credentials later when ready.")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")


def setup_aws_cli():
    """Guide user through AWS CLI configuration."""
    print("\n🔧 AWS CLI Configuration")
    print("-" * 25)
    
    print("\nTo configure AWS CLI, you'll need:")
    print("1. AWS Access Key ID")
    print("2. AWS Secret Access Key")
    print("3. Default region (recommended: us-east-1)")
    
    print("\n📋 Steps to get AWS credentials:")
    print("1. Log into AWS Console (https://console.aws.amazon.com)")
    print("2. Go to IAM > Users > [Your User] > Security credentials")
    print("3. Create access key > Command Line Interface (CLI)")
    print("4. Download or copy the Access Key ID and Secret Access Key")
    
    print("\n⚠️  Important: Keep your credentials secure!")
    print("   - Never commit them to version control")
    print("   - Use IAM roles in production")
    print("   - Rotate keys regularly")
    
    proceed = input("\nDo you have your AWS credentials ready? (y/n): ").strip().lower()
    
    if proceed == 'y':
        print("\n🚀 Run this command to configure AWS CLI:")
        print("   aws configure")
        print("\nThen enter your credentials when prompted:")
        print("   AWS Access Key ID: [Your access key]")
        print("   AWS Secret Access Key: [Your secret key]")
        print("   Default region name: us-east-1")
        print("   Default output format: json")
        
        print("\n✅ After configuration, run the test again:")
        print("   python backend/test_aws_integration.py")
    else:
        print("\n📝 Get your credentials first, then run this script again.")


def setup_environment_variables():
    """Guide user through environment variable setup."""
    print("\n🔧 Environment Variables Setup")
    print("-" * 30)
    
    print("\nYou can set AWS credentials as environment variables:")
    print("\nFor Windows (PowerShell):")
    print("   $env:AWS_ACCESS_KEY_ID='your_access_key_here'")
    print("   $env:AWS_SECRET_ACCESS_KEY='your_secret_key_here'")
    print("   $env:AWS_DEFAULT_REGION='us-east-1'")
    
    print("\nFor Windows (Command Prompt):")
    print("   set AWS_ACCESS_KEY_ID=your_access_key_here")
    print("   set AWS_SECRET_ACCESS_KEY=your_secret_key_here")
    print("   set AWS_DEFAULT_REGION=us-east-1")
    
    print("\nFor Linux/Mac:")
    print("   export AWS_ACCESS_KEY_ID=your_access_key_here")
    print("   export AWS_SECRET_ACCESS_KEY=your_secret_key_here")
    print("   export AWS_DEFAULT_REGION=us-east-1")
    
    print("\n⚠️  Note: Environment variables are temporary and will be lost when you close the terminal.")


def setup_test_credentials():
    """Setup test/demo credentials."""
    print("\n🧪 Test Credentials Setup")
    print("-" * 25)
    
    print("\n⚠️  WARNING: This is for testing only!")
    print("These are not real AWS credentials and will not work with actual AWS services.")
    print("The system will use mock data for demonstration purposes.")
    
    proceed = input("\nProceed with test credentials? (y/n): ").strip().lower()
    
    if proceed == 'y':
        # Set test environment variables
        os.environ['AWS_ACCESS_KEY_ID'] = 'test_access_key_123'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'test_secret_key_456'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        
        print("\n✅ Test credentials set for this session.")
        print("The system will use mock AWS data for testing.")
        print("\n🚀 You can now run:")
        print("   python backend/test_aws_integration.py")
    else:
        print("\n❌ Test credentials setup cancelled.")


def check_current_credentials():
    """Check if AWS credentials are already configured."""
    print("\n🔍 Checking current AWS configuration...")
    
    # Check environment variables
    env_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    env_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    env_region = os.environ.get('AWS_DEFAULT_REGION')
    
    if env_access_key and env_secret_key:
        print("✅ Environment variables found:")
        print(f"   AWS_ACCESS_KEY_ID: {env_access_key[:8]}...")
        print(f"   AWS_SECRET_ACCESS_KEY: {env_secret_key[:8]}...")
        print(f"   AWS_DEFAULT_REGION: {env_region or 'Not set'}")
        return True
    
    # Check AWS CLI configuration
    aws_config_dir = Path.home() / '.aws'
    credentials_file = aws_config_dir / 'credentials'
    config_file = aws_config_dir / 'config'
    
    if credentials_file.exists():
        print("✅ AWS CLI credentials file found:")
        print(f"   {credentials_file}")
        if config_file.exists():
            print(f"   {config_file}")
        return True
    
    print("❌ No AWS credentials found.")
    return False


def test_aws_connection():
    """Test AWS connection after setup."""
    print("\n🧪 Testing AWS Connection...")
    
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError
        
        # Try to create STS client and get caller identity
        sts = boto3.client('sts')
        response = sts.get_caller_identity()
        
        print("✅ AWS Connection successful!")
        print(f"   Account: {response.get('Account', 'Unknown')}")
        print(f"   User ARN: {response.get('Arn', 'Unknown')}")
        
        return True
        
    except NoCredentialsError:
        print("❌ No credentials found. Please configure AWS credentials.")
        return False
    except ClientError as e:
        print(f"❌ AWS Error: {e}")
        return False
    except ImportError:
        print("❌ boto3 not installed. Run: pip install boto3")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting AWS Setup...")
    
    # Check current status
    has_credentials = check_current_credentials()
    
    if has_credentials:
        print("\n🎉 AWS credentials are already configured!")
        
        # Test the connection
        if test_aws_connection():
            print("\n✅ Ready to use AWS services!")
            print("\n🚀 Run the integration test:")
            print("   python backend/test_aws_integration.py")
        else:
            print("\n⚠️  Credentials found but connection failed.")
            print("You may need to reconfigure or check permissions.")
            setup_aws_credentials()
    else:
        # No credentials found, guide through setup
        setup_aws_credentials()
    
    print("\n" + "=" * 55)
    print("🎯 Next Steps:")
    print("1. Ensure AWS credentials are configured")
    print("2. Run: python backend/test_aws_integration.py")
    print("3. Check that required AWS services are enabled")
    print("4. Set up appropriate IAM permissions")
    print("\n📚 For more help, see AWS documentation:")
    print("   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-quickstart.html")