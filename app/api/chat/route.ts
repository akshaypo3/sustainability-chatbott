import { NextResponse } from 'next/server';
import { callColabAI } from '../../../lib/ai-core';

export const runtime = 'edge'; // Recommended for AI applications

export async function POST(request: Request) {
  try {
    const { question } = await request.json();
    
    if (!question || typeof question !== 'string') {
      return NextResponse.json(
        { error: "Invalid question format" },
        { status: 400 }
      );
    }

    const answer = await callColabAI(question);
    return NextResponse.json({ answer });
  } catch (error) {
    console.error("API Error:", error);
    return NextResponse.json(
      { error: "AI service unavailable. Please try again later." },
      { status: 500 }
    );
  }
}