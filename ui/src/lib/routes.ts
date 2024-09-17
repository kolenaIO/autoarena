// TODO: collect various API URLs in this file
import { getAppMode } from '../hooks/useAppMode';

const LOCAL_BASE_API_URL = 'http://localhost:8899/api/v1';

export function getBaseUrl() {
  const { isLocalMode } = getAppMode();
  if (isLocalMode) {
    return LOCAL_BASE_API_URL;
  }
  const pathParts = new URL(window.location.href).pathname.split('/').filter(Boolean);
  const tenant = pathParts.length > 0 ? pathParts[0] : '';
  return `${window.location.origin}/api/v1/${tenant}`;
}

export function getProjectUrl(projectSlug: string) {
  return `${getBaseUrl()}/project/${projectSlug}`;
}
