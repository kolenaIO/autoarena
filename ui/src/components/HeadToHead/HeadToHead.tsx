import { useSearchParams } from 'react-router-dom';
import { Button, Center, Group, Divider, Select, Stack, Paper } from '@mantine/core';
import { useMemo } from 'react';
import { IconClick } from '@tabler/icons-react';
import { prop, sortBy } from 'ramda';
import { useUrlState, useModels } from '../../hooks';
import { NonIdealState } from '../NonIdealState.tsx';
import { APP_CONTENT_WIDTH } from '../constants.ts';
import { HeadToHeadTwoModels } from './HeadToHeadTwoModels.tsx';
import { HeadToHeadSingleModel } from './HeadToHeadSingleModel.tsx';

export function HeadToHead() {
  const { projectSlug } = useUrlState();
  // TODO: migrate this to useUrlState
  const [searchParams, setSearchParams] = useSearchParams();
  const urlModelAId = searchParams.get('modelA');
  const urlModelBId = searchParams.get('modelB');
  const { data: models } = useModels(projectSlug);
  const allSelectModels = useMemo(
    () =>
      sortBy<{ value: string; label: string }>(
        prop('label'),
        (models ?? []).map(({ id, name }) => ({
          value: String(id),
          label: name,
        }))
      ),
    [models]
  );
  const modelA = models?.find(({ id }) => Number(urlModelAId) === id);
  const modelB = models?.find(({ id }) => Number(urlModelBId) === id);

  function onChange(position: 'A' | 'B', newId: number | undefined) {
    const newSearchParams = new URLSearchParams();
    if (position === 'A' && urlModelBId != null) {
      newSearchParams.append('modelB', urlModelBId);
    }
    if (position === 'B' && urlModelAId != null) {
      newSearchParams.append('modelA', urlModelAId);
    }
    if (newId != null) {
      newSearchParams.append(`model${position}`, String(newId));
    }
    setSearchParams(new URLSearchParams(newSearchParams));
  }

  function onRandomize(position: 'A' | 'B') {
    const otherIds = new Set([modelA?.id, modelB?.id].filter(id => id != null));
    // try 100 times to find an ID that doesn't conflict with a selected ID
    for (let i = 0; i < 100; i++) {
      const randomIndex = Math.floor(Math.random() * (models?.length ?? 0));
      const randomId = models?.[randomIndex]?.id;
      if (randomId != null && !otherIds.has(randomId)) {
        onChange(position, randomId);
        return;
      }
    }
  }

  const noModels = allSelectModels.length < 1;
  const noMoreModels = allSelectModels.length - (modelA != null ? 1 : 0) - (modelB != null ? 1 : 0) < 1;
  return (
    <Center p="lg">
      <Stack w={APP_CONTENT_WIDTH}>
        <Group justify="space-between" grow>
          <Group align="flex-end" justify="space-between">
            <Select
              label="Model A"
              placeholder="Select Model"
              data={
                modelB == null
                  ? allSelectModels
                  : allSelectModels.map(option =>
                      option.value === String(modelB.id) ? { ...option, disabled: true } : option
                    )
              }
              value={modelA != null ? String(modelA.id) : undefined}
              onChange={value => onChange('A', value != null ? Number(value) : undefined)}
              disabled={noModels}
              clearable
              searchable
              flex={1}
            />
            <Button variant="light" disabled={noMoreModels} onClick={() => onRandomize('A')}>
              Random
            </Button>
          </Group>
          <Group align="flex-end" justify="space-between">
            <Select
              label="Model B"
              placeholder="Select Model"
              data={
                modelA == null
                  ? allSelectModels
                  : allSelectModels.map(option =>
                      option.value === String(modelA.id) ? { ...option, disabled: true } : option
                    )
              }
              value={modelB != null ? String(modelB.id) : undefined}
              onChange={value => onChange('B', value != null ? Number(value) : undefined)}
              disabled={noModels}
              clearable
              searchable
              flex={1}
            />
            <Button variant="light" disabled={noMoreModels} onClick={() => onRandomize('B')}>
              Random
            </Button>
          </Group>
        </Group>
        <Divider />
        {modelA != null && modelB != null ? (
          <HeadToHeadTwoModels modelAId={modelA.id} modelBId={modelB.id} />
        ) : modelA != null || modelB != null ? (
          <HeadToHeadSingleModel modelId={modelA?.id ?? modelB?.id ?? -1} />
        ) : (
          <Paper withBorder bg="white" p="xl">
            <NonIdealState IconComponent={IconClick} description="Select two models to compare head-to-head" />
          </Paper>
        )}
      </Stack>
    </Center>
  );
}
