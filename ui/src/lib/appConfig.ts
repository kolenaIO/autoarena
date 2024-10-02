import { fetchEventSource, FetchEventSourceInit } from '@microsoft/fetch-event-source';
import { ComponentProps, Context, createContext, useContext } from 'react';
import { CanAccessJudgeStatusIndicator, MainMenu, Judges } from '../components';

export type AppConfig = {
  baseApiUrl: string;
  basePath: string;
  apiFetch: (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
  apiFetchEventSource: (input: RequestInfo, init: FetchEventSourceInit) => Promise<void>;
  propOverrides: Partial<{
    MainMenu: Partial<ComponentProps<typeof MainMenu>>;
    Judges: Partial<ComponentProps<typeof Judges>>;
    CanAccessJudgeStatusIndicator: Partial<ComponentProps<typeof CanAccessJudgeStatusIndicator>>;
  }>;
};

export const DEFAULT_APP_CONFIG: AppConfig = {
  baseApiUrl: 'http://localhost:8899/api/v1',
  basePath: '',
  apiFetch: fetch,
  apiFetchEventSource: fetchEventSource,
  propOverrides: {},
};

export const AppConfigContext: Context<AppConfig> = createContext(DEFAULT_APP_CONFIG);

export function useAppConfig() {
  return useContext(AppConfigContext);
}

export function usePropOverrides<T>(componentName: keyof AppConfig['propOverrides'], defaultProps: T) {
  const { propOverrides } = useAppConfig();
  const overriddenProps = propOverrides[componentName] ?? {};
  return { ...defaultProps, ...overriddenProps };
}
