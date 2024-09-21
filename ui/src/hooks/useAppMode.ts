import { useContext, useMemo } from 'react';
import { AppConfigContext } from '../lib/appConfig.ts';

type AppMode = 'local' | 'cloud';

export function getAppMode() {
  const appMode: AppMode = import.meta.env.MODE === 'cloud' ? 'cloud' : 'local';
  return {
    appMode,
    isLocalMode: appMode === 'local',
    isCloudMode: appMode === 'cloud',
  };
}

export function useAppMode() {
  const { mode } = useContext(AppConfigContext);
  return useMemo(getAppMode, [import.meta.env.MODE]);
}
