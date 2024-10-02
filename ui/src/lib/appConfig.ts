import { fetchEventSource, FetchEventSourceInit } from '@microsoft/fetch-event-source';
import { Context, createContext, useContext } from 'react';

type PropOverrideKey = React.JSXElementConstructor<never>;
type PropOverrideValue = { [key: string]: unknown };

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
  propOverrides: new Map(),
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
