// TODO: collect various API URLs in this file
import { getAppMode } from '../hooks/useAppMode';

const LOCAL_BASE_API_URL = 'http://localhost:8899/api/v1';

function getTenantName() {
  const pathParts = new URL(window.location.href).pathname.split('/').filter(Boolean);
  return pathParts.length > 0 ? pathParts[0] : undefined;
}

export function getBaseApiUrl() {
  const { isLocalMode } = getAppMode();
  return isLocalMode ? LOCAL_BASE_API_URL : `${window.location.origin}/api/v1/${getTenantName()}`;
}

export function getProjectApiUrl(projectSlug: string) {
  return `${getBaseApiUrl()}/project/${projectSlug}`;
}

function getBasePath() {
  const { isLocalMode } = getAppMode();
  return isLocalMode ? '' : `/${getTenantName()}`;
}

export const ROUTES = {
  home: () => `${getBasePath()}/`,
  leaderboard: (projectSlug: string) => `${getBasePath()}/project/${projectSlug}`,
  compare: (projectSlug: string) => `${getBasePath()}/project/${projectSlug}/compare`,
  judges: (projectSlug: string) => `${getBasePath()}/project/${projectSlug}/judges`,
};
