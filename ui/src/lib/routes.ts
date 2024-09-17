// TODO: collect various API URLs in this file
import { getAppMode } from '../hooks/useAppMode.ts';

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

export enum ExternalUrls {
  AUTOARENA_GITHUB = 'https://github.com/kolenaIO/autoarena',
  AUTOARENA_GITHUB_ISSUES = 'https://github.com/kolenaIO/autoarena/issues/new',
  AUTOARENA_SLACK_COMMUNITY = 'https://kolena-autoarena.slack.com',

  TOGETHER_MODELS = 'https://docs.together.ai/docs/chat-models',
  OLLAMA_MODELS = 'https://ollama.com/library',
  BEDROCK_MODELS = 'https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html',
  OPENAI_BASE_URL_README = 'https://github.com/openai/openai-python#configuring-the-http-client',
}
