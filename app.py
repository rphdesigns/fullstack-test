#!/usr/bin/env python3
from aws_cdk import App
from stacks.api_stack import ApiStack
from stacks.web_stack import WebStack

app = App()

web_domain = app.node.try_get_context("web_domain")
cloudfront_cert_arn = app.node.try_get_context("cloudfront_cert_arn")

api_stack = ApiStack(
    app,
    "ApiStack"
)

web_stack = WebStack(
    app,
    "WebStack",
    # api_endpoint=api_stack.api_endpoint
)

app.synth()
