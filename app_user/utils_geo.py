# app_user/utils_geo.py
import os
import geoip2.database
import requests
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

GEOIP_DB_PATH = getattr(settings, "GEOIP_PATH", None)
GEOIP_DB_FILE = os.path.join(GEOIP_DB_PATH, "GeoLite2-Country.mmdb") if GEOIP_DB_PATH else None
CACHE_TIMEOUT = 60 * 60  # 1 soat

def get_client_ip(request):
    """
    Get client IP, supporting multiple headers.
    Priority: X-Real-IP > CF-Connecting-IP > X-Forwarded-For > REMOTE_ADDR
    """
    for header in ("HTTP_X_REAL_IP", "HTTP_CF_CONNECTING_IP", "HTTP_X_FORWARDED_FOR", "REMOTE_ADDR"):
        ip = request.META.get(header)
        if ip:
            # X-Forwarded-For bir nechta IP bo'lishi mumkin
            if header == "HTTP_X_FORWARDED_FOR":
                ip = ip.split(",")[0].strip()
            logger.info(f"Detected client IP from {header}: {ip}")
            return ip.strip()
    logger.warning("No client IP found, defaulting to None")
    return None

def country_code_from_ip(ip):
    """
    Returns ISO country code from IP.
    1. Cache
    2. Local GeoIP DB
    3. ipapi.co fallback
    """
    if not ip:
        return None

    cache_key = f"ip_country_{ip}"
    cached = cache.get(cache_key)
    if cached:
        logger.info(f"Country from cache for {ip}: {cached}")
        return cached

    # 1️⃣ Local GeoIP DB
    if GEOIP_DB_FILE and os.path.exists(GEOIP_DB_FILE):
        try:
            with geoip2.database.Reader(GEOIP_DB_FILE) as reader:
                response = reader.country(ip)
                country_code = (response.country.iso_code or "").upper()
                if country_code:
                    cache.set(cache_key, country_code, CACHE_TIMEOUT)
                    logger.info(f"Country from GeoIP DB for {ip}: {country_code}")
                    return country_code
        except Exception as e:
            logger.exception(f"GeoIP DB lookup failed for {ip}: {e}")

    # 2️⃣ Fallback: external API
    try:
        r = requests.get(f"https://ipapi.co/{ip}/country/", timeout=3)
        if r.status_code == 200:
            country_code = r.text.strip().upper()
            cache.set(cache_key, country_code, CACHE_TIMEOUT)
            logger.info(f"Country from ipapi.co for {ip}: {country_code}")
            return country_code
        else:
            logger.warning(f"ipapi.co returned {r.status_code} for {ip}")
    except Exception as e:
        logger.exception(f"ipapi.co lookup failed for {ip}: {e}")

    logger.warning(f"Unable to determine country for {ip}")
    return None

def is_ip_from_uz(request):
    """
    Returns True if client IP belongs to Uzbekistan.
    Localhost (127.0.0.1, 192.168.x.x, etc.) is treated as UZ in DEBUG mode.
    """
    ip = get_client_ip(request)

    # 👇 Lokal test muhitida doim True (UZ) sifatida qaytarish
    if settings.DEBUG and ip and (
        ip in ("127.0.0.1", "::1") or ip.startswith(("192.168.", "10."))
    ):
        logger.info(f"Local IP {ip} treated as UZ (DEBUG mode).")
        return True

    # 🌍 Productionda real GeoIP orqali tekshirish
    country = country_code_from_ip(ip)
    logger.info(f"is_ip_from_uz check: IP={ip}, country={country}")

    return country == "UZ"