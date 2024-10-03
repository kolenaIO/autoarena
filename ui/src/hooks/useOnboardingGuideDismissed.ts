import { readLocalStorageValue, useLocalStorage } from '@mantine/hooks';
import { useEffect } from 'react';

export function useOnboardingGuideDismissed(projectSlug: string | undefined) {
  const key = `/project/${projectSlug}/onboarding-guide-dismissed`;
  const deserialize = (value: string | undefined) => value === 'true';

  const out = useLocalStorage<boolean>({
    key,
    defaultValue: false,
    deserialize,
    serialize: value => (value ? 'true' : 'false'),
  });

  // manually reset value when key changes; useLocalStorage does not handle this itself
  useEffect(() => {
    const [, setValue] = out;
    setValue(readLocalStorageValue({ key, defaultValue: false, deserialize }));
  }, [key]);

  return out;
}
