import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { useEffect } from 'react';
import { notifications } from '@mantine/notifications';

type Params<T> = {
  errorTitle?: string;
  errorMessage: string;
} & UseQueryOptions<T>;
export function useQueryWithErrorToast<T>({ errorTitle, errorMessage, ...options }: Params<T>) {
  const { error, ...query } = useQuery(options);

  useEffect(() => {
    if (error != null) {
      notifications.show({ title: errorTitle, message: errorMessage, color: 'red', id: errorMessage });
    }
  }, [errorTitle, errorMessage, error]);

  return { error, ...query };
}
