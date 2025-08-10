# Deploy notes

1. Ensure Route53 hosted zone exists for your domain.

Example CDK deploy command (replace values):
```
cdk deploy --all -c hosted_zone=example.com -c web_domain=www.example.com -c api_domain=api.example.com -c cloudfront_cert_arn=arn:aws:acm:us-east-1:123:certificate/xxx -c api_cert_arn=arn:aws:acm:us-west-2:123:certificate/yyy
```

In GitHub Actions, the workflow will:
- build Angular (production)
- deploy the CDK stacks
- read CloudFormation outputs (site bucket & distribution)
- sync `frontend/dist` to S3 and invalidate CloudFront
