// TODO: collect various API URLs in this file
export const BASE_API_URL = 'http://localhost:8899/api/v1';

export function getProjectUrl(projectSlug: string) {
  return `${BASE_API_URL}/project/${projectSlug}`;
}

export enum ExternalUrls {
  TOGETHER_MODELS = 'https://docs.together.ai/docs/chat-models',
  OLLAMA_MODELS = 'https://ollama.com/library',
  BEDROCK_MODELS = 'https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html',
}
