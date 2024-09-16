import { Task } from '../hooks/useTasks.ts';

export function taskIsDone(taskStatus: Task['status']) {
  return taskStatus === 'completed' || taskStatus === 'failed';
}

export function taskStatusToLabel(taskStatus: Task['status']) {
  switch (taskStatus) {
    case 'started':
      return 'Started';
    case 'in-progress':
      return 'In Progress';
    case 'completed':
      return 'Completed';
    case 'failed':
      return 'Failed';
  }
}

export function taskStatusToColor(taskStatus: Task['status']) {
  switch (taskStatus) {
    case 'started':
      return 'gray';
    case 'in-progress':
      return 'cyan';
    case 'completed':
      return 'green';
    case 'failed':
      return 'red';
  }
}
