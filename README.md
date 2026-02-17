# pulumi-aws-infra
Example Infrastructure as Code (IaC) set up using pulumi to deploy AWS resources. Uses himl for hierarchical config to configure deployment for multiple stage and region.

## Getting Started
Before using this package, make sure you have already create the [Pulumi AWS Infra Bootstrap](https://github.com/pcyang/pulumi-aws-infra-bootstrap)
After creating the bootstrap, copy over the S3 bucket path and the KMS key and save them to `.devcontainer/personal.env`.
```
PULUMI_STATE_BUCKET=s3://<bucket-name>
PULUMI_STATE_KMS_KEY=awskms://1234abcd-12ab-34cd-56ef-1234567890ab?region=us-west-2
```

After that, you need to set up your aws credential. As of 02/16/2026, `aws login` doesn't seems to be picked up by Pulumi. I ended up using `aws configure` to populate my AWS Access and Secret key from an IAM User on my local machine then have it mounted as readonly on the devcontainer. Will update the repo if I find a better alternative.

## Creating new environment
Here's an example of how to create a new environment. The stack name is in the format of <env>.<region>.
```
pulumi stack init dev.us-west-2 \
    --secrets-provider="$PULUMI_STATE_KMS_KEY"
```

## Configuring environment
You can configure the by modifying or adding to `config/`. That uses [himl](https://github.com/adobe/himl) which provide hierarchical configuration. Everything is inherited from `defaults.yaml` and each environment and region can have their own overrides.

To expand on this infrastructure package, you can add more of your own stack following the existing convention. You can also modify `static_website_config.py` to make more of Static Website stack configurable.