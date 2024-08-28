import { Center, Checkbox, Table } from '@mantine/core';
import { useState } from 'react';
import { useModels } from './useModels.ts';

export function Home() {
  const [selectedRows, setSelectedRows] = useState<number[]>([]);
  const { data: models = [] } = useModels();
  return (
    <Center p="lg">
      <Table stickyHeader striped withTableBorder highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            <Table.Th />
            <Table.Th>ID</Table.Th>
            <Table.Th>Name</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {models.map((model, i) => (
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
              <Table.Td>{model.id}</Table.Td>
              <Table.Td>{model.name}</Table.Td>
            </Table.Tr>
          ))}
        </Table.Tbody>
      </Table>
    </Center>
  );
}
