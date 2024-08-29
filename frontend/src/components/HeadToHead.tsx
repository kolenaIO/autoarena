import { useSearchParams } from 'react-router-dom';
import { Button, Center, Group, Divider, Select, Stack } from '@mantine/core';
import { useMemo } from 'react';
import { useModels } from './useModels.ts';
import { HeadToHeadBattle } from './HeadToHeadBattle.tsx';

export function HeadToHead() {
  const [searchParams, setSearchParams] = useSearchParams();
  const urlModelAId = searchParams.get('modelA');
  const urlModelBId = searchParams.get('modelB');
  const { data: models } = useModels();
  const allSelectModels = useMemo(
    () =>
      (models ?? []).map(({ id, name }) => ({
        value: String(id),
        label: name,
      })),
    [models]
  );
  const modelA = models?.find(({ id }) => Number(urlModelAId) === id);
  const modelB = models?.find(({ id }) => Number(urlModelBId) === id);

  function onChange(position: 'A' | 'B', newId: number | undefined) {
    const existingParams =
      position === 'A'
        ? urlModelBId != null
          ? { modelB: urlModelBId }
          : {}
        : urlModelAId != null
          ? { modelA: urlModelAId }
          : {};
    const newParams = newId == null ? {} : position === 'A' ? { modelA: newId } : { modelB: newId };
    setSearchParams(new URLSearchParams({ ...existingParams, ...newParams }));
  }

  function onRandomize(position: 'A' | 'B') {
    const randomIndex = Math.floor(Math.random() * (models?.length ?? 0));
    const randomId = models?.[randomIndex]?.id;
    onChange(position, randomId);
  }

  return (
    <Center p="lg">
      <Stack w={1080} /* TODO: should be max width */>
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
              onChange={value => onChange('A', value)}
              searchable
              flex={1}
            />
            <Button variant="light" onClick={() => onRandomize('A')}>
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
              onChange={value => onChange('B', value)}
              searchable
              flex={1}
            />
            <Button variant="light" onClick={() => onRandomize('B')}>
              Random
            </Button>
          </Group>
        </Group>
        {modelA != null && modelB != null && (
          <>
            <Divider />
            <HeadToHeadBattle modelAId={modelA.id} modelBId={modelB.id} />
          </>
        )}
      </Stack>
    </Center>
  );
}
