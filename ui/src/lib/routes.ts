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

export const API_ROUTES = {
  getProjects: () => `${getBaseApiUrl()}/projects`,
  createProject: () => `${getBaseApiUrl()}/project`,
  deleteProject: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}`,
  getModels: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/models`,
  getModelsRankedByJudge: (projectSlug: string, judgeId: number) =>
    `${getProjectApiUrl(projectSlug)}/models/by-judge/${judgeId}`,
  uploadModelResponses: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/model`,
  getModelResponse: (projectSlug: string, modelId: number) => `${getProjectApiUrl(projectSlug)}/model/${modelId}/judge`,
  triggerModelAutoJudge: (projectSlug: string, modelId: number) =>
    `${getProjectApiUrl(projectSlug)}/model/${modelId}/judge`,
  deleteModel: (projectSlug: string, modelId: number) => `${getProjectApiUrl(projectSlug)}/model/${modelId}`,
  downloadModelResponsesCsv: (projectSlug: string, modelId: number) =>
    `${getProjectApiUrl(projectSlug)}/model/${modelId}/download/responses`,
  downloadModelHeadToHeadsCsv: (projectSlug: string, modelId: number) =>
    `${getProjectApiUrl(projectSlug)}/model/${modelId}/download/head-to-heads`,
  getHeadToHeadStats: (projectSlug: string, modelId: number) =>
    `${getProjectApiUrl(projectSlug)}/model/${modelId}/head-to-head/stats`,
  getHeadToHeads: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/head-to-heads`,
  getHeadToHeadCount: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/head-to-head/count`,
  submitHeadToHeadVote: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/head-to-head/vote`,
  getTasks: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/tasks`,
  getTaskStream: (projectSlug: string, taskId: number) => `${getProjectApiUrl(projectSlug)}/task/${taskId}/stream`,
  getHasActiveTasksStream: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/tasks/has-active`,
  deleteCompletedTasks: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/tasks/completed`,
  triggerAutoJudge: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/task/auto-judge`,
  getJudges: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/judges`,
  getDefaultSystemPrompt: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/judge/default-system-prompt`,
  createJudge: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/judge`,
  updateJudge: (projectSlug: string, judgeId: number) => `${getProjectApiUrl(projectSlug)}/judge/${judgeId}`,
  checkCanAccess: (projectSlug: string, judgeType: string) =>
    `${getProjectApiUrl(projectSlug)}/judge/${judgeType}/can-access`, // TODO: use enum type?
  deleteJudge: (projectSlug: string, judgeId: number) => `${getProjectApiUrl(projectSlug)}/judge/${judgeId}`,
  reseedEloScores: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/elo/reseed-scores`,
  createFineTuningTask: (projectSlug: string) => `${getProjectApiUrl(projectSlug)}/fine-tune`,
};
