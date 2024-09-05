import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

export function useUrlState() {
  const { projectId: projectIdFromUrl } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const projectId = projectIdFromUrl != null ? Number(projectIdFromUrl) : undefined;
  function setProjectId(newProjectId: number | null | undefined) {
    navigate(newProjectId != null ? `/project/${newProjectId}` : '/');
  }

  const judgeIdFromUrl = searchParams.get('judgeId');
  const judgeId: number | undefined = judgeIdFromUrl != null ? Number(judgeIdFromUrl) : undefined;
  function setJudgeId(newJudgeId: number | null | undefined) {
    const newSearchParams = new URLSearchParams(searchParams);
    newSearchParams.delete('judgeId');
    if (newJudgeId != null) {
      newSearchParams.append('judgeId', String(newJudgeId));
    }
    setSearchParams(newSearchParams);
  }

  return { projectId, setProjectId, judgeId, setJudgeId };
}
