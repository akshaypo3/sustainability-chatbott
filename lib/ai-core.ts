export async function callColabAI(question: string): Promise<string> {
  // This will be replaced with your SAP AI Core endpoint after deployment
  const endpoint = process.env.SAP_AI_ENDPOINT || "ttps://119775931ea0.ngrok-free.app/predict";
  
  try {
    const response = await fetch("http://localhost:5000/v1/predict", {
      method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: question }) // Same as working PowerShell example
});

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}`);
    }

    const data = await response.json();
    
    if (data.status === "error") {
      throw new Error(data.error || "Unknown error from AI service");
    }

    return data.answer || "I didn't understand that question. Could you rephrase?";
  } catch (error) {
    console.error("API Error:", error);
    return "I'm having trouble connecting to the knowledge base. Please try again later.";
  }
}