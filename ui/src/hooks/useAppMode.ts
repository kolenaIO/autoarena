import { useMemo } from 'react';

type AppMode = 'local' | 'cloud';

export function useAppMode() {
  return useMemo(() => {
    const appMode: AppMode = import.meta.env.MODE === 'cloud' ? 'cloud' : 'local';
    return {
      appMode,
      isLocalMode: appMode === 'local',
      isCloudMode: appMode === 'cloud',
    };
  }, [import.meta.env.MODE]);
}
