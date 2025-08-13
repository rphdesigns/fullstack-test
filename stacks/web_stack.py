from aws_cdk import (
    Stack,
    CfnOutput,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_route53 as route53,
    aws_certificatemanager as acm,
    aws_route53_targets as targets
)
from constructs import Construct

HOSTED_ZONE_NAME = "app-rphdesigns.com"  # Replace with your actual hosted zone name
WEB_DOMAIN = "api.app-rphdesigns.com"  # Replace with your actual API domain


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
            validation=acm.CertificateValidation.from_dns(hosted_zone)
        )

        distribution = cloudfront.Distribution(
            self,
            "SiteDistribution",
            default_root_object="index.html",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_identity(site_bucket, origin_access_identity=oai),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=[WEB_DOMAIN],
            certificate=cert
        )

        # Route53 mapping
        route53.CfnRecordSet(
            self,
            "SiteAliasRecord",
            hosted_zone_id=hosted_zone.hosted_zone_id,
            name=WEB_DOMAIN,
            type="A",
            alias_target=route53.CfnRecordSet.AliasTargetProperty(
                dns_name=distribution.distribution_domain_name,
                hosted_zone_id=hosted_zone.hosted_zone_id # Standard CloudFront hosted zone ID
            )
        )

        CfnOutput(self, "SiteBucketName", value=site_bucket.bucket_name)
        CfnOutput(self, "CloudFrontDomain", value=distribution.distribution_domain_name)
        CfnOutput(self, "SiteURL", value=f"https://{WEB_DOMAIN}")
