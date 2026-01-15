const BACKEND_URL = "http://127.0.0.1:8000";

export async function askQuestion(question, token) {
  const response = await fetch(`${BACKEND_URL}/qa`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ question })
  });

  if (!response.ok) {
    throw new Error("Failed to get answer");
  }

  return response.json();
}
