"""Domain configuration packages — product/index/routing/policy assets."""

from domains.loader import get_default_domain, load_domain
from domains.models import DomainConfig

__all__ = ["DomainConfig", "get_default_domain", "load_domain"]
