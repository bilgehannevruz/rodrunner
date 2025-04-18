#!/usr/bin/env python3
"""
Test script for iRODS connection.
"""
import os
import sys
import time
from irods.session import iRODSSession
from irods.exception import CAT_INVALID_AUTHENTICATION, NetworkException

def test_irods_connection(host, port, user, password, zone, max_retries=5, retry_delay=5):
    """
    Test connection to iRODS server with retries.

    Args:
        host: iRODS host
        port: iRODS port
        user: iRODS user
        password: iRODS password
        zone: iRODS zone
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds

    Returns:
        True if connection successful, False otherwise
    """
    print(f"Testing connection to iRODS server at {host}:{port}")
    print(f"User: {user}, Zone: {zone}")

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}...")
            with iRODSSession(host=host, port=port, user=user, password=password, zone=zone) as session:
                # Try to list collections in the home directory
                coll_path = f"/{zone}/home/{user}"
                print(f"Listing collections in {coll_path}")
                colls = list(session.collections.get(coll_path).subcollections)
                print(f"Found {len(colls)} collections:")
                for coll in colls:
                    print(f"  {coll.name}")

                # Try to create a test collection
                test_coll_name = f"test_collection_{int(time.time())}"
                test_coll_path = f"{coll_path}/{test_coll_name}"
                print(f"Creating test collection: {test_coll_path}")
                session.collections.create(test_coll_path)
                print(f"Test collection created successfully")

                # Try to remove the test collection
                print(f"Removing test collection: {test_coll_path}")
                session.collections.remove(test_coll_path)
                print(f"Test collection removed successfully")

                print("iRODS connection test successful!")
                return True

        except CAT_INVALID_AUTHENTICATION:
            print("Authentication failed. Check your username, password, and zone.")
            return False

        except NetworkException as e:
            print(f"Network error: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum retries reached. Connection failed.")
                return False

        except Exception as e:
            print(f"Error: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum retries reached. Connection failed.")
                return False

    return False


if __name__ == "__main__":
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Test connection to iRODS server.")
    parser.add_argument("--host", default=os.environ.get("IRODS_HOST", "localhost"),
                        help="iRODS host (default: %(default)s)")
    parser.add_argument("--port", type=int, default=int(os.environ.get("IRODS_PORT", "1247")),
                        help="iRODS port (default: %(default)s)")
    parser.add_argument("--user", default=os.environ.get("IRODS_USER", "rods"),
                        help="iRODS user (default: %(default)s)")
    parser.add_argument("--password", default=os.environ.get("IRODS_PASSWORD", "rods"),
                        help="iRODS password (default: %(default)s)")
    parser.add_argument("--zone", default=os.environ.get("IRODS_ZONE", "tempZone"),
                        help="iRODS zone (default: %(default)s)")
    parser.add_argument("--max-retries", type=int, default=5,
                        help="Maximum number of retries (default: %(default)s)")
    parser.add_argument("--retry-delay", type=int, default=5,
                        help="Delay between retries in seconds (default: %(default)s)")

    args = parser.parse_args()

    # Test connection
    success = test_irods_connection(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        zone=args.zone,
        max_retries=args.max_retries,
        retry_delay=args.retry_delay
    )

    # Exit with appropriate status code
    sys.exit(0 if success else 1)
