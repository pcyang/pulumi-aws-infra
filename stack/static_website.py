import pulumi
from pulumi_aws import (s3, cloudfront)
import pulumi_aws as aws
import pulumi_synced_folder as synced_folder

from stack.static_website_config import StaticWebsiteConfig


class StaticWebsite(pulumi.ComponentResource):
    s3_url: pulumi.Output[str]
    cdn_url: pulumi.Output[str]

    def __init__(
            self,
            static_website_config: StaticWebsiteConfig,
            env: str,
            region: str,
            opts=None):
        super().__init__('pkg:index:StaticWebsite', static_website_config.name, None, opts)

        current_caller_identity = aws.get_caller_identity()
        account_id = current_caller_identity.account_id

        # Create an S3 bucket and configure it as a website.
        bucket_name = f"{static_website_config.name}-{account_id}-{region}-{env}"
        bucket = s3.Bucket(
            bucket_name,
            opts=pulumi.ResourceOptions(parent=self),
        )
        bucket_web_config = s3.BucketWebsiteConfiguration(
            f"{bucket_name}-web-config",
            bucket=bucket.id,
            index_document=aws.s3.BucketWebsiteConfigurationIndexDocumentArgs(
                suffix=static_website_config.index_document,
            ),
            error_document=aws.s3.BucketWebsiteConfigurationErrorDocumentArgs(
                key=static_website_config.error_document,
            ),
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Set ownership controls for the new bucket
        ownership_controls = s3.BucketOwnershipControls(
            f"{bucket_name}-ownership-controls",
            bucket=bucket.bucket,
            rule={
                "object_ownership": "ObjectWriter",
            },
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Configure public ACL block on the new bucket
        public_access_block = s3.BucketPublicAccessBlock(
            f"{bucket_name}-public-access-block",
            bucket=bucket.bucket,
            block_public_acls=False,
            opts=pulumi.ResourceOptions(parent=self),
        )

        # Use a synced folder to manage the files of the website.
        bucket_folder = synced_folder.S3BucketFolder(
            f"{bucket_name}-folder",
            acl="public-read",
            bucket_name=bucket.bucket,
            path=static_website_config.path,
            opts=pulumi.ResourceOptions(
                depends_on=[ownership_controls, public_access_block],
                parent=self,),
        )

        # AWS recommend using S3 website endpoint rather than
        # the bucket endpoint
        self.s3_url = pulumi.Output.concat(
            bucket.bucket, ".s3-website-", region, ".amazonaws.com"
        )
        self.s3_full_url = pulumi.Output.concat(
            "http://", self.s3_url)

        # Create a CloudFront CDN to distribute and cache the website.
        cdn = cloudfront.Distribution(
            f"{bucket_name}-cdn",
            enabled=True,
            origins=[
                {
                    "origin_id": bucket.arn,
                    "domain_name": self.s3_url,
                    "origin_path": static_website_config.cdn_config.origin_path,
                    "custom_origin_config": {
                        "origin_protocol_policy": "http-only",
                        "http_port": 80,
                        "https_port": 443,
                        "origin_ssl_protocols": ["TLSv1.2"],
                    },
                }
            ],
            default_cache_behavior={
                "target_origin_id": bucket.arn,
                "viewer_protocol_policy": "redirect-to-https",
                "allowed_methods": [
                    "GET",
                    "HEAD",
                    "OPTIONS",
                ],
                "cached_methods": [
                    "GET",
                    "HEAD",
                    "OPTIONS",
                ],
                "default_ttl": 600,
                "max_ttl": 600,
                "min_ttl": 600,
                "forwarded_values": {
                    "query_string": True,
                    "cookies": {
                        "forward": "all",
                    },
                },
            },
            # Set the default root object
            default_root_object=static_website_config.index_document,
            price_class="PriceClass_100",
            custom_error_responses=[
                {
                    "error_code": 404,
                    "response_code": 404,
                    "response_page_path": f"/{static_website_config.error_document}",
                }
            ],
            restrictions={
                "geo_restriction": {
                    "restriction_type": "none",
                },
            },
            viewer_certificate={
                "cloudfront_default_certificate": True,
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        # Export the URLs and hostnames of the bucket and distribution.
        self.cdn_url = pulumi.Output.concat("https://", cdn.domain_name)
        pulumi.export("originURL", self.s3_full_url)
        pulumi.export("originHostname", self.s3_url)
        pulumi.export("cdnURL", self.cdn_url)
        pulumi.export("cdnHostname", cdn.domain_name)

        # Registering Component Outputs
        self.register_outputs({
            "s3_url": self.s3_url,
            "cdn_url": self.cdn_url,
        })
