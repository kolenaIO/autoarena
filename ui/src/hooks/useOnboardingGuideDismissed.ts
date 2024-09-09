import { useLocalStorage } from '@mantine/hooks';

export function useOnboardingGuideDismissed(projectSlug: string | undefined) {
  return useLocalStorage<boolean>({
    key: `/project/${projectSlug}/onboarding-guide-dismissed`,
    defaultValue: false,
    deserialize: value => value === 'true',
    serialize: value => (value ? 'true' : 'false'),
  });
}
