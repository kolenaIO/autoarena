export type AppMode = 'local' | 'cloud';

export function useAppMode(): AppMode {
  return import.meta.env.MODE === 'cloud' ? 'cloud' : 'local';
}
