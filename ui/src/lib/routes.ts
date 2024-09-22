type HTTPVerb = 'GET' | 'PUT' | 'POST' | 'DELETE';

export function urlAsQueryKey(url: string, method: HTTPVerb | undefined = 'GET') {
  const urlObject = new URL(url);
  return [urlObject.origin, ...urlObject.pathname.split('/').filter(Boolean), ...(method != null ? [method] : [])];
}
