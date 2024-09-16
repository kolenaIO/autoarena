import { useEffect, useState } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { getProjectUrl } from '../lib/routes.ts';

export function useHasActiveTasksStream(projectSlug?: string) {
  const [hasActiveTasks, setHasActiveTasks] = useState(false);
  const controller = new AbortController();

  useEffect(() => {
    if (projectSlug == null) {
      return;
    }
    const fetchData = async () => {
      // TODO: add proper abort controller
      await fetchEventSource(`${getProjectUrl(projectSlug)}/tasks/has-active`, {
        method: 'GET',
        headers: { Accept: 'text/event-stream' },
        signal: controller.signal,
        onmessage: event => {
          const parsedData: { has_active: boolean } = JSON.parse(event.data);
          setHasActiveTasks(parsedData.has_active);
        },
      });
    };
    fetchData();
  }, [projectSlug]);

  return hasActiveTasks;
}
