#!/usr/bin/env python3
import os
from aws_cdk import App
from stacks.api_stack import ApiStack
from stacks.web_stack import WebStack

app = App()

web_domain = app.node.try_get_context("web_domain")
cloudfront_cert_arn = app.node.try_get_context("cloudfront_cert_arn")

env = {
    "account": app.node.try_get_context("cdk_account") or os.environ.get("CDK_DEFAULT_ACCOUNT"),
    "region": app.node.try_get_context("cdk_region") or os.environ.get("CDK_DEFAULT_REGION"),
}

api_stack = ApiStack(
    app,
    "ApiStack",
    env=env
)

web_stack = WebStack(
    app,
    "WebStack",
    env=env
    # api_endpoint=api_stack.api_endpoint
)

app.synth()
