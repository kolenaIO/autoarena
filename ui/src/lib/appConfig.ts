import { fetchEventSource, FetchEventSourceInit } from '@microsoft/fetch-event-source';
import { Context, createContext } from 'react';
import { JudgeType } from '../components';

export type AppConfig = {
  baseApiUrl: string;
  basePath: string;
  apiFetch: (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
  apiFetchEventSource: (input: RequestInfo, init: FetchEventSourceInit) => Promise<void>;
  enabledJudges: JudgeType[];
};

export const DEFAULT_APP_CONFIG: AppConfig = {
  baseApiUrl: 'http://localhost:8899/api/v1',
  basePath: '',
  apiFetch: fetch,
  apiFetchEventSource: fetchEventSource,
  enabledJudges: ['ollama', 'openai', 'anthropic', 'gemini', 'cohere', 'together', 'bedrock'],
};

export const AppConfigContext: Context<AppConfig> = createContext(DEFAULT_APP_CONFIG);
