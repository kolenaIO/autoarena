import { fetchEventSource, FetchEventSourceInit } from '@microsoft/fetch-event-source';
import { Context, createContext, useContext } from 'react';
import { Judges, MainMenu } from '../components';

type PropOverrideKey = React.JSXElementConstructor<any>;
type PropOverrideValue = { [key: string]: any };

export type AppConfig = {
  baseApiUrl: string;
  basePath: string;
  apiFetch: (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;
  apiFetchEventSource: (input: RequestInfo, init: FetchEventSourceInit) => Promise<void>;
  propOverrides: Map<PropOverrideKey, PropOverrideValue>;
};

export const DEFAULT_APP_CONFIG: AppConfig = {
  baseApiUrl: 'http://localhost:8899/api/v1',
  basePath: '',
  apiFetch: fetch,
  apiFetchEventSource: fetchEventSource,
  propOverrides: new Map([
    [MainMenu, { extraMenuItems: ['foobar'] }],
    [Judges, { enabledJudges: ['openai'] }],
  ] as [PropOverrideKey, PropOverrideValue][]),
};

export const AppConfigContext: Context<AppConfig> = createContext(DEFAULT_APP_CONFIG);

export function useAppConfig() {
  return useContext(AppConfigContext);
}

export function usePropOverrides<T>(Component: React.JSXElementConstructor<T>, defaultProps: T) {
  const { propOverrides } = useAppConfig();
  const overriddenProps = propOverrides.has(Component) ? propOverrides.get(Component) : {};
  return { ...defaultProps, ...overriddenProps };
}
