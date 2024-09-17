import { useMemo } from 'react';

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
  return useMemo(getAppMode, [import.meta.env.MODE]);
}
