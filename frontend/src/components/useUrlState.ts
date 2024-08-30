import { useNavigate, useParams } from 'react-router-dom';

export function useUrlState() {
  const { projectId: projectIdFromUrl } = useParams();
  const navigate = useNavigate();

  const projectId = projectIdFromUrl != null ? Number(projectIdFromUrl) : undefined;
  function setProjectId(newProjectId: number | null) {
    navigate(newProjectId != null ? `/project/${newProjectId}` : '/');
  }

  return { projectId, setProjectId };
}
