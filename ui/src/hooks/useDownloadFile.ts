import { useMutation } from '@tanstack/react-query';
import { urlAsQueryKey, useAppConfig } from '../lib';

export function useDownloadFile(url: string, fileName: string) {
  const { apiFetch } = useAppConfig();
  return useMutation({
    mutationKey: urlAsQueryKey(url),
    mutationFn: async () => {
      const response = await apiFetch(url);
      if (!response.ok) {
        throw new Error('Failed to download file');
      }
      const a = document.createElement('a');
      a.setAttribute('download', fileName);
      a.href = URL.createObjectURL(await response.blob());
      a.click();
    },
  });
}
