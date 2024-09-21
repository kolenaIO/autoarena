type HTTPVerb = 'GET' | 'PUT' | 'POST' | 'DELETE';

export function urlAsQueryKey(url: string, method: HTTPVerb = 'GET') {
  const urlObject = new URL(url);
  return [urlObject.origin, ...urlObject.pathname.split('/').filter(Boolean), method];
}
