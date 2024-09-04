import { useLocalStorage } from '@mantine/hooks';

export function useOnboardingGuideDismissed(projectId: number | undefined) {
  return useLocalStorage<boolean>({
    key: `/project/${projectId}/onboarding-guide-dismissed`,
    defaultValue: false,
    deserialize: value => value === 'true',
    serialize: value => (value ? 'true' : 'false'),
  });
}
