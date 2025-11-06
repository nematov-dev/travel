# app_user/utils_geo.py
import os
import geoip2.database
import requests
from django.conf import settings
from django.core.cache import cache

GEOIP_DB_PATH = getattr(settings, "GEOIP_PATH", None)
GEOIP_DB_FILE = os.path.join(GEOIP_DB_PATH, "GeoLite2-Country.mmdb") if GEOIP_DB_PATH else None
CACHE_TIMEOUT = 60 * 60  # 1 soat (IP -> country mapping cache)

def get_client_ip(request):
    """Get client IP respecting proxy headers. Only trust X-Forwarded-For if behind trusted proxy."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0].strip()
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def country_code_from_ip(ip):
    """
    Get country code from IP.
    1) Try cache first.
    2) Use local GeoIP DB.
    3) Fallback to external API (ipapi.co)
    """
    if not ip:
        return None

    cache_key = f"ip_country_{ip}"
    cached_country = cache.get(cache_key)
    if cached_country:
        return cached_country

    # 1) Local GeoIP DB
    if GEOIP_DB_FILE and os.path.exists(GEOIP_DB_FILE):
        try:
            with geoip2.database.Reader(GEOIP_DB_FILE) as reader:
                response = reader.country(ip)
                if response and response.country and response.country.iso_code:
                    country_code = response.country.iso_code.upper()
                    cache.set(cache_key, country_code, CACHE_TIMEOUT)
                    return country_code
        except Exception:
            pass

    # 2) Fallback: external API
    try:
        r = requests.get(f"https://ipapi.co/{ip}/country/", timeout=3)
        if r.status_code == 200:
            country_code = r.text.strip().upper()
            cache.set(cache_key, country_code, CACHE_TIMEOUT)
            return country_code
    except Exception:
        pass

    return None

def is_ip_from_uz(request):
    """
    Returns True if request IP belongs to Uzbekistan (country code 'UZ').
    """
    ip = get_client_ip(request)
    country = country_code_from_ip(ip)
    return country == "UZ"
