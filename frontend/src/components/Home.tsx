import { Center, Checkbox, Table } from '@mantine/core';
import { useMemo, useState } from 'react';
import moment from 'moment';
import { useModels } from './useModels.ts';

export function Home() {
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const { data: models = [] } = useModels();
  const modelsSorted = useMemo(() => models.sort((a, b) => b.elo - a.elo), [models]);

  return (
    <Center p="lg">
      <Table stickyHeader striped withTableBorder highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th />
            <Table.Th>Rank</Table.Th>
            <Table.Th>Name</Table.Th>
            <Table.Th>Created</Table.Th>
            <Table.Th>Elo</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {modelsSorted.map((model, i) => (
            <Table.Tr
              key={i}
              bg={selectedRows.includes(model.id) ? 'var(--mantine-color-kolena-light)' : undefined}
              onclick={() => {
                console.log('clicked', model.id);
              }}
            >
              <Table.Td>
                <Checkbox
                  checked={selectedRows.includes(model.id)}
                  onChange={event => {
                    setSelectedRows(
                      event.currentTarget.checked
                        ? [...selectedRows, model.id]
                        : selectedRows.filter(id => id !== model.id)
                    );
                  }}
                />
              </Table.Td>
              <Table.Td>{i + 1}</Table.Td>
              <Table.Td>{model.name}</Table.Td>
              <Table.Td>{moment(model.created).format('YYYY-MM-DD (hh:mm A)')}</Table.Td>
              <Table.Td>{model.elo.toFixed(1)}</Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </Center>
  );
}
