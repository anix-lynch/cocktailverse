#!/usr/bin/env python3
# 💬 PHASE 1: Cloud Function Entry Point
# Purpose: Main entry point for Cloud Function (Gen2)
#
# Outputs:
#   - HTTP response with transformation status
#
# Sample Output:
#   {"statusCode": 200, "message": "Data transformed successfully"}

import functions_framework
from transform import main

@functions_framework.cloud_event
def cloud_function_handler(cloud_event):
    """
    Cloud Function Gen2 entry point for GCS events
    """
    return main(cloud_event)

