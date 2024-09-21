import { useAuth0 } from '@auth0/auth0-react';
import { fetchEventSource, FetchEventSourceInit } from '@microsoft/fetch-event-source';
import { AUTH0 } from '../lib';
import { useAppMode } from './useAppMode.ts';

export function useApiFetch() {
  const { isLocalMode } = useAppMode();
  const { getAccessTokenSilently, logout } = useAuth0();

  async function apiFetch(input: RequestInfo | URL, init?: RequestInit | undefined) {
    const token = await getAccessTokenSilently({ authorizationParams: { audience: AUTH0.API_AUDIENCE } });
    const response = await fetch(input, {
      ...init,
      headers: { ...init?.headers, Authorization: `Bearer ${token}` },
    });
    if (response.status === 401) {
      await logout({ logoutParams: { returnTo: window.location.origin } });
    }
    return response;
  }

  async function apiFetchEventSource(input: RequestInfo, init?: FetchEventSourceInit | undefined) {
    const token = await getAccessTokenSilently({ authorizationParams: { audience: AUTH0.API_AUDIENCE } });
    await fetchEventSource(input, {
      ...init,
      headers: { ...init?.headers, Authorization: `Bearer ${token}` },
    });
  }

  return isLocalMode ? { apiFetch: fetch, apiFetchEventSource: fetchEventSource } : { apiFetch, apiFetchEventSource };
}
