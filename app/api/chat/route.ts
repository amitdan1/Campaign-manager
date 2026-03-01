import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/db";
import { chat, isOpenAIAvailable } from "@/lib/openai";
import { chatMessageSchema } from "@/lib/validation";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const parsed = chatMessageSchema.safeParse(body);
    if (!parsed.success) {
      return NextResponse.json(
        { success: false, error: "Message is required (1-2000 chars)" },
        { status: 400 }
      );
    }

    const { message } = parsed.data;

    // Save user message
    await prisma.chatMessage.create({
      data: { role: "user", content: message },
    });

    let responseText: string;
    let agentName = "Orchestrator";

    if (isOpenAIAvailable()) {
      const systemPrompt = `You are the Orchestrator for a performance marketing system for Ofir Assulin Interior Design.
You manage marketing agents: lead capture, lead scoring, content creation, campaign management, landing pages, and strategy.
Answer in Hebrew. Be concise and actionable.
If the user asks to do something, explain what you can help with.`;

      const result = await chat(systemPrompt, message, {
        maxTokens: 800,
        endpoint: "chat",
      });

      responseText = result ?? "מצטער, לא הצלחתי לעבד את הבקשה. נסה שוב.";
    } else {
      responseText = "שירות ה-AI לא מוגדר. הגדר OPENAI_API_KEY בהגדרות הסביבה.";
    }

    // Save agent response
    await prisma.chatMessage.create({
      data: { role: "agent", agentName, content: responseText },
    });

    return NextResponse.json({
      success: true,
      response: responseText,
      agent: agentName,
    });
  } catch (e) {
    return NextResponse.json({ success: false, error: String(e) }, { status: 500 });
  }
}
