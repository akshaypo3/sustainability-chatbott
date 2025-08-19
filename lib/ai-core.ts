// lib/ai-core.ts
export async function callSAPAI(question: string): Promise<string> {
  // 1. First try SAP AI Core (replace with your actual SAP endpoint later)
  const SAP_ENDPOINT = "YOUR_FUTURE_SAP_ENDPOINT"; // 👈 Will update after SAP deployment
  const COLAB_ENDPOINT = "https://fd88ff9c3ee6.ngrok-free.app/predict"; // 👈 Your current ngrok URL

  try {
    // Phase 1: Test with Colab while SAP deploys
    const response = await fetch(COLAB_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: question })
    });
    
    const data = await response.json();
    return data.answer || "I didn't understand that question.";

  } catch (error) {
    console.error("API Error:", error);
    return "Connection failed. Please try again later.";
  }
}