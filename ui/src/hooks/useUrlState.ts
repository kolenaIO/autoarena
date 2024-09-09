import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

export function useUrlState() {
  const { projectSlug: projectSlugFromUrl } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const projectSlug = typeof projectSlugFromUrl === 'string' ? projectSlugFromUrl : undefined;
  function setProjectSlug(newProjectSlug: string | null | undefined) {
    navigate(newProjectSlug != null ? `/project/${newProjectSlug}` : '/');
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

  return { projectSlug, setProjectSlug, judgeId, setJudgeId };
}
