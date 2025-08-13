from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    aws_route53 as route53,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as api_gw,
    aws_apigatewayv2_integrations_alpha as api_gw_integrations,
    aws_certificatemanager as acm,
    aws_route53_targets as route53_targets,
)
from constructs import Construct

API_DOMAIN = "api.example.com"  # Replace with your actual API domain
HOSTED_ZONE_NAME = "example.com"  # Replace with your actual hosted zone name


class ApiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB table for items
        table = dynamodb.Table(
            self,
            "ItemsTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            removal_policy=kwargs.get("removal_policy")
        )

        # Lambda function (single handler for CRUD)
        handler = _lambda.Function(
            self, "ApiHandler",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="handler.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            timeout=Duration.seconds(10),
            memory_size=256,
            environment={
                "TABLE_NAME": table.table_name,
            }
        )

        # grant lambda access to table
        table.grant_read_write_data(handler)

        # HTTP API
        http_api = api_gw.HttpApi(
            self,
            "HttpApi",
            api_name="ItemsHttpApi"
        )

        integration = api_gw_integrations.HttpLambdaIntegration("LambdaIntegration", handler)
        # routes
        http_api.add_routes(
            path="/items",
            methods=[api_gw.HttpMethod.GET, api_gw.HttpMethod.POST],
            integration=integration
        )
        http_api.add_routes(
            path="/items/{id}",
            methods=[api_gw.HttpMethod.GET, api_gw.HttpMethod.PUT, api_gw.HttpMethod.DELETE],
            integration=integration
        )

        self.api = http_api
        self.api_endpoint = http_api.api_endpoint
        CfnOutput(self, "HttpApiEndpoint", value=self.api_endpoint)

        # Custom domain + Route53 mapping + ACM certificate
        hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name=HOSTED_ZONE_NAME)

        # Create ACM certificate in us-east-1 for API Gateway
        cert = acm.Certificate(
            self,
            "ApiCert",
            domain_name=API_DOMAIN,
            validation=acm.CertificateValidation.from_dns(hosted_zone)
        )
        api_domain_obj = api_gw.DomainName(self, "ApiDomain", domain_name=API_DOMAIN, certificate=cert)
        api_gw.HttpApiMapping(self, "ApiMapping", domain_name=api_domain_obj, api=http_api, stage=http_api.default_stage)

        route53.ARecord(
            self,
            "ApiAliasRecord",
            zone=hosted_zone,
            record_name=API_DOMAIN.split(".")[0],
            target=route53.RecordTarget.from_alias(route53_targets.ApiGatewayv2Domain(api_domain_obj))
        )
        CfnOutput(self, "ApiCustomDomain", value=API_DOMAIN)
