import { Button, Card, Portal, Stack, Text } from '@mantine/core';
import { useNavigate } from 'react-router-dom';
import { useAppRoutes, useUrlState } from '../../hooks';
import { RankedModel } from './types.ts';

type Props = {
  selectedModels: RankedModel[];
};
export function ExploreSelectedModels({ selectedModels }: Props) {
  const { projectSlug } = useUrlState();
  const { appRoutes } = useAppRoutes();
  const navigate = useNavigate();

  function handleGoCompare() {
    const modelA = selectedModels[0];
    const modelB = selectedModels[1];
    if ((modelA == null && modelB == null) || projectSlug == null) {
      return;
    }
    const params = new URLSearchParams();
    if (modelA != null) {
      params.append('modelA', String(modelA.id));
    }
    if (modelB != null) {
      params.append('modelB', String(modelB.id));
    }
    navigate(`${appRoutes.compare(projectSlug)}?${params}`);
  }

  return (
    <Portal>
      <Card
        withBorder
        shadow="md"
        style={{
          position: 'fixed',
          zIndex: 10,
          width: 400,
          bottom: 24,
          right: 'calc(50% - 200px)',
          left: 'calc(50% - 200px)',
        }}
      >
        <Stack>
          <Text>
            Explore{' '}
            <Text span inherit c="blue.6">
              {selectedModels[0]?.name}
            </Text>
            {selectedModels?.length < 2 ? (
              ':'
            ) : (
              <>
                {' '}
                vs.{' '}
                <Text span inherit c="orange.6">
                  {selectedModels[1]?.name}
                </Text>
                :
              </>
            )}
          </Text>
          <Button disabled={selectedModels.length < 1} onClick={handleGoCompare}>
            {selectedModels.length === 1 ? 'View Responses' : 'Compare Head-to-Head'}
          </Button>
        </Stack>
      </Card>
    </Portal>
  );
}
