import pulumi

from stack.static_website import StaticWebsite
from stack.static_website_config import StaticWebsiteConfig
from utils import config_loader

stack = pulumi.get_stack()
parts = stack.split(".")
env = parts[0]
region = parts[1]

config = config_loader.load_config(env, region)


if "static_website_config" in config:
    static_website_config = StaticWebsiteConfig(
        **config["static_website_config"])
    static_website_component = StaticWebsite(
        static_website_config=static_website_config,
        env=env,
        region=region,)
