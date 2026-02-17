"""
Brand Scraper Agent (pure automation).
Periodically scrapes Ofir's website, Instagram, Facebook, TikTok.
Downloads images, extracts text/style, and stores them as BrandAssets.
"""

import os
import re
import hashlib
import logging
from typing import Any, Dict, List
from datetime import datetime

import requests

from agents.base_agent import BaseAgent
from models.brand_asset import BrandAsset
from services.database import get_session

logger = logging.getLogger("agent.BrandScraper")

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "brand_assets")


class BrandScraperAgent(BaseAgent):
    """Scrapes Ofir's digital presence and builds a brand asset library."""

    def __init__(self):
        super().__init__(name="BrandScraper")
        os.makedirs(os.path.join(ASSETS_DIR, "images"), exist_ok=True)

    def run(self, sources: List[str] = None, **kwargs) -> Dict[str, Any]:
        """
        Scrape brand assets from all configured sources.
        sources: list of sources to scrape (default: all).
        """
        sources = sources or ["website"]
        results = {}

        if "website" in sources:
            results["website"] = self._scrape_website()

        # Instagram / Facebook / TikTok require API tokens;
        # for now, mark them as not-configured but structurally ready.
        if "instagram" in sources:
            results["instagram"] = self._scrape_instagram()
        if "facebook" in sources:
            results["facebook"] = self._scrape_facebook()
        if "tiktok" in sources:
            results["tiktok"] = self._scrape_tiktok()

        total = sum(r.get("new_assets", 0) for r in results.values())
        return {
            "success": True,
            "total_new_assets": total,
            "sources": results,
        }

    # --- Website Scraper ---

    def _scrape_website(self) -> dict:
        """Scrape images and text from ofirassulin.design."""
        url = self.config.BUSINESS_WEBSITE
        self.logger.info(f"Scraping website: {url}")

        try:
            resp = requests.get(url, timeout=15,
                                headers={"User-Agent": "Mozilla/5.0 (compatible; MarketingBot/1.0)"})
            resp.raise_for_status()
            html = resp.text
        except Exception as e:
            self.logger.error(f"Failed to fetch website: {e}")
            return {"available": True, "new_assets": 0, "error": str(e)}

        # Extract image URLs from Wix-style static images
        img_urls = re.findall(
            r'(https://static\.wixstatic\.com/media/[^\s"\']+\.(?:jpg|jpeg|png|webp))',
            html,
            re.IGNORECASE,
        )

        # Deduplicate by base URL (ignore query params)
        seen = set()
        unique_urls = []
        for img_url in img_urls:
            base = img_url.split("?")[0].split("/v1/")[0] if "/v1/" in img_url else img_url.split("?")[0]
            if base not in seen:
                seen.add(base)
                unique_urls.append(img_url)

        # Extract text blocks
        text_blocks = re.findall(r'<(?:h[1-6]|p)[^>]*>([^<]{20,})</(?:h[1-6]|p)>', html)

        new_assets = 0
        session = get_session()
        try:
            # Store images
            for img_url in unique_urls[:30]:  # Limit to 30 images
                if self._asset_exists(session, img_url):
                    continue

                local_path = self._download_image(img_url, "website")
                if local_path:
                    asset = BrandAsset(
                        asset_type="image",
                        source="website",
                        url=img_url,
                        local_path=local_path,
                        asset_metadata={"alt": "", "page": url},
                    )
                    session.add(asset)
                    new_assets += 1

            # Store notable text
            for text in text_blocks[:10]:
                clean = text.strip()
                if len(clean) > 20 and not self._asset_exists(session, clean):
                    asset = BrandAsset(
                        asset_type="text",
                        source="website",
                        url=url,
                        asset_metadata={"content": clean},
                    )
                    session.add(asset)
                    new_assets += 1

            session.commit()
            self.logger.info(f"Website scrape complete: {new_assets} new assets")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error storing website assets: {e}")
            return {"available": True, "new_assets": 0, "error": str(e)}
        finally:
            session.close()

        return {"available": True, "new_assets": new_assets, "images": len(unique_urls)}

    # --- Social Media (placeholder implementations) ---

    def _scrape_instagram(self) -> dict:
        if not self.config.is_facebook_configured():
            return {"available": False, "new_assets": 0, "message": "Instagram API not configured. Set FACEBOOK_ACCESS_TOKEN in .env."}
        # TODO: Implement with Instagram Basic Display API or instaloader
        return {"available": True, "new_assets": 0, "message": "Instagram scraping not yet implemented"}

    def _scrape_facebook(self) -> dict:
        if not self.config.is_facebook_configured():
            return {"available": False, "new_assets": 0, "message": "Facebook API not configured"}
        # TODO: Implement with Facebook Graph API
        return {"available": True, "new_assets": 0, "message": "Facebook scraping not yet implemented"}

    def _scrape_tiktok(self) -> dict:
        return {"available": False, "new_assets": 0, "message": "TikTok API not configured"}

    # --- Helpers ---

    def _download_image(self, url: str, source: str) -> str:
        """Download an image and return the local path."""
        try:
            url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
            ext = "jpg"
            for e in (".png", ".webp", ".jpeg"):
                if e in url.lower():
                    ext = e.replace(".", "")
                    break

            filename = f"{source}_{url_hash}.{ext}"
            filepath = os.path.join(ASSETS_DIR, "images", filename)

            if os.path.exists(filepath):
                return f"/brand_assets/images/{filename}"

            resp = requests.get(url, timeout=10, stream=True,
                                headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)

            return f"/brand_assets/images/{filename}"
        except Exception as e:
            self.logger.warning(f"Failed to download {url}: {e}")
            return ""

    def _asset_exists(self, session, url_or_text: str) -> bool:
        """Check if an asset with this URL already exists."""
        return session.query(BrandAsset).filter(BrandAsset.url == url_or_text).first() is not None

    def health_check(self) -> Dict[str, Any]:
        asset_dir_exists = os.path.isdir(ASSETS_DIR)
        session = get_session()
        try:
            count = session.query(BrandAsset).count()
        except Exception:
            count = 0
        finally:
            session.close()

        return {
            "healthy": True,
            "asset_directory": asset_dir_exists,
            "total_assets": count,
        }
