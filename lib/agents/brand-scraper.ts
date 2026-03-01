import { prisma } from "@/lib/db";
import { config } from "@/lib/config";

export async function scrapeAssets() {
  // In the full implementation this would scrape the business website,
  // Instagram, Facebook, etc. For Vercel, images would be stored in Vercel Blob.
  // For now, we do a basic website metadata scrape.

  try {
    const url = config.business.website;
    if (!url) return { success: false, error: "No business website configured" };

    const response = await fetch(url, {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; MarketingBot/1.0)" },
    });

    if (!response.ok) {
      return { success: false, error: `Failed to fetch website: ${response.status}` };
    }

    const html = await response.text();

    // Extract images
    const imgRegex = /<img[^>]+src=["']([^"']+)["']/gi;
    const images: string[] = [];
    let match;
    while ((match = imgRegex.exec(html)) !== null) {
      const src = match[1];
      if (src.startsWith("http") && !src.includes("favicon")) {
        images.push(src);
      }
    }

    let saved = 0;
    for (const imgUrl of images.slice(0, 20)) {
      const exists = await prisma.brandAsset.findFirst({ where: { url: imgUrl } });
      if (!exists) {
        await prisma.brandAsset.create({
          data: {
            assetType: "image",
            source: "website",
            url: imgUrl,
            assetMetadata: JSON.stringify({ scrapedFrom: url }),
          },
        });
        saved++;
      }
    }

    return { success: true, found: images.length, saved };
  } catch (e) {
    console.error("Scraper error:", e);
    return { success: false, error: String(e) };
  }
}

export async function getAssets(filters: { source?: string; assetType?: string } = {}) {
  return prisma.brandAsset.findMany({
    where: {
      ...(filters.source ? { source: filters.source } : {}),
      ...(filters.assetType ? { assetType: filters.assetType } : {}),
    },
    orderBy: { createdAt: "desc" },
  });
}
