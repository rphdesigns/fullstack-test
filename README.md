# CDK Python + Angular Full Scaffold (Lambda + DynamoDB + API Gateway + S3 + CloudFront + Route53)

This scaffold includes:
- AWS CDK (Python) app that deploys:
  - Lambda-backed HTTP API with DynamoDB table (CRUD)
  - S3 bucket + CloudFront + Route53 for Angular frontend
- Angular frontend (minimal) with CRUD UI against the API
- GitHub Actions workflow to build frontend, deploy CDK infra, sync frontend to S3 and invalidate CloudFront

**NOTES BEFORE DEPLOY**
- You must supply ACM certificate ARNs, hosted zone, domain names via CDK context or adjust `app.py`.
- Add GitHub secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_ACCOUNT_ID`.
- The Angular app reads the API base URL from `src/environments/environment.prod.ts` at build time. CI sets this during build using the API endpoint output.

See `cdk.json` and `README_DEPLOY.md` for deploy instructions.
