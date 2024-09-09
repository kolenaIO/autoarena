// TODO: collect various API URLs in this file
export const BASE_API_URL = 'http://localhost:8899/api/v1';

export const API = {
  GET_PROJECTS: `${BASE_API_URL}/projects`,
  CREATE_PROJECT: `${BASE_API_URL}/project`,
  DELETE_PROJECT: `${BASE_API_URL}/project`,
  GET_MODELS: (projectSlug: string) => `${BASE_API_URL}/project/${projectSlug}/models`,
};
