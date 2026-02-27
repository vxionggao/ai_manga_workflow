# Copyright (c) 2025 Beijing Volcano Engine Technology Co., Ltd. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import tos
from tos import HttpMethodType

# Import consts from project root
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
# Try to import constants, use defaults if fails
try:
    from consts import DEFAULT_BUCKET, DEFAULT_REGION
except ImportError:
    DEFAULT_BUCKET = "manju-test"
    DEFAULT_REGION = "cn-beijing"

# Try to import veadk auth utils
try:
    from veadk.auth.veauth.utils import get_credential_from_vefaas_iam
except ImportError:
    # Fallback or dummy implementation if veadk is not available
    def get_credential_from_vefaas_iam():
        raise ImportError("veadk not installed")

logger = logging.getLogger(__name__)


def upload_file_to_tos(
    file_path: str,
    bucket_name: Optional[str] = None,
    object_key: Optional[str] = None,
    region: Optional[str] = None,
    ak: Optional[str] = None,
    sk: Optional[str] = None,
    session_token: Optional[str] = None,
    expires: int = 604800,  # 7-day validity
) -> Optional[str]:
    """
    Upload a file to TOS object storage and return a signed accessible URL

    Args:
        file_path: Local file path
        bucket_name: TOS bucket name, defaults to "aaa-bbb-ccc-ddd"
        object_key: Object storage key name; if empty, uses the filename
        region: TOS region, defaults to cn-beijing
        ak: Access Key; if empty, reads from environment variables
        sk: Secret Key; if empty, reads from environment variables
        expires: Signed URL validity period (seconds), defaults to 7 days (604800 seconds)

    Returns:
        str: Signed TOS URL that can be accessed directly
        None: Returns None if upload fails

    Environment variables required:
        VOLCENGINE_ACCESS_KEY: Volcano Engine access key
        VOLCENGINE_SECRET_KEY: Volcano Engine secret key

    Usage example:
        >>> url = upload_file_to_tos("./video.mp4")
        >>> print(url)
        https://bucket.tos-cn-beijing.volces.com/video.mp4?X-Tos-Signature=...
    """

    if bucket_name is None:
        bucket_name = os.getenv("DATABASE_TOS_BUCKET")
        if bucket_name is None:
            bucket_name = DEFAULT_BUCKET
            logger.info(
                f"Warn: bucket_name is not provided in env, using default bucket name: {bucket_name}"
            )
        else:
            logger.info(f"Using bucket_name from env: {bucket_name}")
    if region is None:
        region = os.getenv("DATABASE_TOS_REGION")
        if region is None:
            region = DEFAULT_REGION
            logger.info(
                f"Warn: region is not provided in env, using default region: {region}"
            )
        else:
            logger.info(f"Using region from env: {region}")

    # Check if file exists
    if not os.path.exists(file_path):
        logger.info(f"Error: File does not exist: {file_path}")
        return None

    if not os.path.isfile(file_path):
        logger.info(f"Error: Path is not a file: {file_path}")
        return None

    # Retrieve STS from IAM Role
    access_key = os.getenv("VOLCENGINE_ACCESS_KEY")
    secret_key = os.getenv("VOLCENGINE_SECRET_KEY")
    session_token = ""

    if not (access_key and secret_key):
        try:
            # try to get from vefaas iam
            cred = get_credential_from_vefaas_iam()
            access_key = cred.access_key_id
            secret_key = cred.secret_access_key
            session_token = cred.session_token
        except Exception:
            pass

    if not access_key or not secret_key:
        logger.info(
            "Error: VOLCENGINE_ACCESS_KEY and VOLCENGINE_SECRET_KEY are not provided or IAM Role is not configured."
        )
        return None

    # Auto-generate object_key (using filename)
    if not object_key:
        # Combine timestamp and original filename to avoid overwriting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        if ext:
            object_key = f"upload/{name}_{timestamp}{ext}"
        else:
            object_key = f"upload/{filename}_{timestamp}"

    # Create TOS client
    client = None
    try:
        # Initialize TOS client
        endpoint = f"tos-{region}.volces.com"
        client = tos.TosClientV2(
            ak=access_key,
            sk=secret_key,
            security_token=session_token,
            endpoint=endpoint,
            region=region,
        )

        logger.info(f"Starting file upload: {file_path}")
        logger.info(f"Target Bucket: {bucket_name}")
        logger.info(f"Object Key: {object_key}")

        # Ensure bucket exists (create if not)
        try:
            client.head_bucket(bucket_name)
            logger.info(f"Bucket {bucket_name} already exists")
        except tos.exceptions.TosServerError as e:
            if e.status_code == 404:
                logger.info(f"Bucket {bucket_name} does not exist, creating...")
                client.create_bucket(bucket_name)
            else:
                raise e

        # Upload file
        result = client.put_object_from_file(
            bucket=bucket_name, key=object_key, file_path=file_path
        )

        logger.info("File uploaded successfully!")
        logger.info(f"ETag: {result.etag}")
        logger.info(f"Request ID: {result.request_id}")

        # Generate signed URL
        signed_url_output = client.pre_signed_url(
            http_method=HttpMethodType.Http_Method_Get,
            bucket=bucket_name,
            key=object_key,
            expires=expires,
        )

        signed_url = signed_url_output.signed_url
        logger.info(f"Signed URL generated successfully (valid for {expires} seconds)")
        logger.info(f"Access URL: {signed_url}")

        return signed_url

    except tos.exceptions.TosClientError as e:
        logger.info(f"TOS client error: {e}")
        return None
    except tos.exceptions.TosServerError as e:
        logger.info(f"TOS server error: {e}")
        logger.info(f"Status code: {e.status_code}")
        logger.info(f"Error code: {e.code}")
        logger.info(f"Error message: {e.message}")
        return None
    except Exception as e:
        logger.info(f"File upload failed: {e}")
        import traceback

        traceback.print_exc()
        return None
    finally:
        # Close client
        if client:
            client.close()
