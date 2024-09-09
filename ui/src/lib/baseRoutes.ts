// TODO: collect various API URLs in this file
export const BASE_API_URL = 'http://localhost:8899/api/v1';

export function getProjectUrl(projectSlug: string) {
  return `${BASE_API_URL}/project/${projectSlug}`;
}
