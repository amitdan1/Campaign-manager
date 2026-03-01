import { prisma } from "@/lib/db";

export async function createTest(name: string, variants: Array<{ proposalId: number; variantName: string; weight?: number }>) {
  const test = await prisma.aBTest.create({
    data: {
      name,
      variants: {
        create: variants.map((v) => ({
          proposalId: v.proposalId,
          variantName: v.variantName,
          weight: v.weight ?? 1 / variants.length,
        })),
      },
    },
    include: { variants: true },
  });
  return test;
}

export async function getAllTests() {
  return prisma.aBTest.findMany({
    include: { variants: true },
    orderBy: { createdAt: "desc" },
  });
}

export async function getTestResults(testId: number) {
  const test = await prisma.aBTest.findUnique({
    where: { id: testId },
    include: { variants: true },
  });
  if (!test) return null;

  const variants = test.variants.map((v) => ({
    ...v,
    conversionRate: v.views > 0 ? (v.conversions / v.views) * 100 : 0,
  }));

  return { ...test, variants };
}

export async function endTest(testId: number) {
  return prisma.aBTest.update({
    where: { id: testId },
    data: { status: "completed", endedAt: new Date() },
    include: { variants: true },
  });
}

export async function recordView(testId: number, variantId: number) {
  await prisma.aBTestVariant.update({
    where: { id: variantId },
    data: { views: { increment: 1 } },
  });
}

export async function recordConversion(testId: number, variantId: number) {
  await prisma.aBTestVariant.update({
    where: { id: variantId },
    data: { conversions: { increment: 1 } },
  });
}
