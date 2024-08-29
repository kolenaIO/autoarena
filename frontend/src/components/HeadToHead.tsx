import { useSearchParams } from 'react-router-dom';
import { Center, Group, Select, Stack } from '@mantine/core';
import { useMemo } from 'react';
import { useModels } from './useModels.ts';

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

  return (
    <Center p="lg">
      <Stack w={1080} /* TODO: should be max width */>
        <Group justify="space-between" grow>
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
          />
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
          />
        </Group>
        <div>
          comparing: {modelA?.name} {modelB?.name}
        </div>
      </Stack>
    </Center>
  );
}
