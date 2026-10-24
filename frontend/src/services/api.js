const BASE_URL = `${import.meta.env.BACKEND_URL}/api`;

export async function sendChatMessage(message, conversationId = null, context = {}) {
  const response = await fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      conversation_id: conversationId,
      context,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server error (${response.status})`);
  }

  return response.json();
}

export async function fetchPolicyStatus() {
  const response = await fetch(`${BASE_URL}/policy/status`);
  if (!response.ok) {
    throw new Error('Failed to retrieve policy status');
  }
  return response.json();
}

export async function fetchPolicySections() {
  const response = await fetch(`${BASE_URL}/policy/sections`);
  if (!response.ok) {
    throw new Error('Failed to retrieve policy sections');
  }
  return response.json();
}

export async function fetchPolicySourceDetail(sourceId) {
  const response = await fetch(`${BASE_URL}/policy/source/${encodeURIComponent(sourceId)}`);
  if (!response.ok) {
    throw new Error('Failed to retrieve source detail');
  }
  return response.json();
}

export async function triggerReindex(adminToken) {
  const response = await fetch(`${BASE_URL}/policy/reindex`, {
    method: 'POST',
    headers: {
      'X-Admin-Token': adminToken,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to trigger re-index');
  }

  return response.json();
}
