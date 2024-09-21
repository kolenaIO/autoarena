import { useContext } from 'react';
import { JudgeType } from '../components';
import { AppConfigContext } from '../lib';

// TODO: should this be part of AppConfig itself?
export function useRoutes() {
  const { baseApiUrl, basePath } = useContext(AppConfigContext);

  const appRoutes = {
    home: () => `${basePath}/`,
    leaderboard: (projectSlug: string) => `${basePath}/project/${projectSlug}`,
    compare: (projectSlug: string) => `${basePath}/project/${projectSlug}/compare`,
    judges: (projectSlug: string) => `${basePath}/project/${projectSlug}/judges`,
  };

  const apiRoutes = {
    getProjects: () => `${baseApiUrl}/projects`,
    createProject: () => `${baseApiUrl}/project`,
    deleteProject: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}`,
    getModels: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/models`,
    getModelsRankedByJudge: (projectSlug: string, judgeId: number) =>
      `${baseApiUrl}/project/${projectSlug}/models/by-judge/${judgeId}`,
    uploadModelResponses: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/model`,
    getModelResponses: (projectSlug: string, modelId: number) =>
      `${baseApiUrl}/project/${projectSlug}/model/${modelId}/responses`,
    triggerModelAutoJudge: (projectSlug: string, modelId: number) =>
      `${baseApiUrl}/project/${projectSlug}/model/${modelId}/judge`,
    deleteModel: (projectSlug: string, modelId: number) => `${baseApiUrl}/project/${projectSlug}/model/${modelId}`,
    downloadModelResponsesCsv: (projectSlug: string, modelId: number) =>
      `${baseApiUrl}/project/${projectSlug}/model/${modelId}/download/responses`,
    downloadModelHeadToHeadsCsv: (projectSlug: string, modelId: number) =>
      `${baseApiUrl}/project/${projectSlug}/model/${modelId}/download/head-to-heads`,
    getHeadToHeadStats: (projectSlug: string, modelId: number) =>
      `${baseApiUrl}/project/${projectSlug}/model/${modelId}/head-to-head/stats`,
    getHeadToHeads: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/head-to-heads`,
    getHeadToHeadCount: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/head-to-head/count`,
    submitHeadToHeadVote: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/head-to-head/vote`,
    getTasks: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/tasks`,
    getTaskStream: (projectSlug: string, taskId: number) =>
      `${baseApiUrl}/project/${projectSlug}/task/${taskId}/stream`,
    getHasActiveTasksStream: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/tasks/has-active`,
    deleteCompletedTasks: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/tasks/completed`,
    triggerAutoJudge: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/task/auto-judge`,
    getJudges: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/judges`,
    getDefaultSystemPrompt: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/judge/default-system-prompt`,
    createJudge: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/judge`,
    updateJudge: (projectSlug: string, judgeId: number) => `${baseApiUrl}/project/${projectSlug}/judge/${judgeId}`,
    downloadJudgeVotesCsv: (projectSlug: string, judgeId: number) =>
      `${baseApiUrl}/project/${projectSlug}/judge/${judgeId}/download/votes`,
    checkCanAccess: (projectSlug: string, judgeType: JudgeType) =>
      `${baseApiUrl}/project/${projectSlug}/judge/${judgeType}/can-access`,
    deleteJudge: (projectSlug: string, judgeId: number) => `${baseApiUrl}/project/${projectSlug}/judge/${judgeId}`,
    reseedEloScores: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/elo/reseed-scores`,
    createFineTuningTask: (projectSlug: string) => `${baseApiUrl}/project/${projectSlug}/fine-tune`,
  };

  return { appRoutes, apiRoutes };
}
