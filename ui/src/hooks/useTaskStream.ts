import { useEffect, useState } from 'react';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { getProjectUrl } from '../lib/routes.ts';
import { Task } from './useTasks.ts';

export function useTaskStream(projectSlug: string, task: Task, enabled: boolean) {
  const [taskFromStream, setTaskFromStream] = useState<Task>(task);
  const controller = new AbortController();

  useEffect(() => {
    if (!enabled) {
      return;
    }
    const fetchData = async () => {
      // TODO: add proper abort controller
      await fetchEventSource(`${getProjectUrl(projectSlug)}/task/${task.id}/stream`, {
        method: 'GET',
        headers: { Accept: 'text/event-stream' },
        signal: controller.signal,
        onmessage: event => {
          const parsedData: Task = JSON.parse(event.data);
          setTaskFromStream(parsedData);
        },
      });
    };
    fetchData();
  }, [task.id, enabled]);

  return taskFromStream;
}
