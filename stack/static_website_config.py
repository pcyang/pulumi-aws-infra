from pydantic import BaseModel


class CDNConfig(BaseModel):
    default_ttl: int = 600
    max_ttl: int = 600
    min_ttl: int = 600
    origin_path: str = ""


class StaticWebsiteConfig(BaseModel):
    name: str
    path: str
    index_document: str
    error_document: str
    cdn_config: CDNConfig = CDNConfig()
