from aws_cdk import (
    Stack,
    CfnOutput,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_certificatemanager as acm,
    aws_route53_targets as route53_targets
)
from constructs import Construct

HOSTED_ZONE_NAME = "example.com"  # Replace with your actual hosted zone name
WEB_DOMAIN = "www.example.com"  # Replace with your actual web domain


class WebStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        site_bucket = s3.Bucket(
            self,
            "SiteBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            removal_policy=kwargs.get("removal_policy")
        )

        # CloudFront OAI
        oai = cloudfront.OriginAccessIdentity(self, "OAI")
        site_bucket.grant_read(oai)

        # Certificate
        cert = None
        hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name=HOSTED_ZONE_NAME)
        cert = acm.Certificate(
            self,
            "CloudFrontCert",
            domain_name=WEB_DOMAIN,
            validation=acm.CertificateValidation.from_dns(hosted_zone),
            region="us-east-1"  # CloudFront requires certs in us-east-1
        )

        distribution = cloudfront.Distribution(
            self,
            "SiteDistribution",
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(site_bucket, origin_access_identity=oai),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=[WEB_DOMAIN],
            certificate=cert
        )

        # Route53 mapping
        route53.ARecord(
            self,
            "SiteAliasRecord",
            zone=hosted_zone,
            record_name=WEB_DOMAIN.split(".")[0],
            target=route53.RecordTarget.from_alias(route53_targets.CloudFrontTarget(distribution))
        )

        CfnOutput(self, "SiteBucketName", value=site_bucket.bucket_name)
        CfnOutput(self, "CloudFrontDomain", value=distribution.distribution_domain_name)
        CfnOutput(self, "SiteURL", value=f"https://{WEB_DOMAIN}")
