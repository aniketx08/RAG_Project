const BACKEND_URL = "http://127.0.0.1:8000";

export async function askQuestion(payload, token) {
  const res = await fetch(`${BACKEND_URL}/qa`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error("QA failed");
  }

  return res.json();
}

export async function fetchChats(token) {
  const res = await fetch("http://127.0.0.1:8000/chats", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) throw new Error("Failed to fetch chats");

  return res.json();
}

