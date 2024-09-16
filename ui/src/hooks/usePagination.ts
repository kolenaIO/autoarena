import { useEffect, useState } from 'react';
import { HotkeyItem, useHotkeys } from '@mantine/hooks';

type Params<T> = {
  records: T[];
  withHotkeys?: boolean;
};
export function usePagination<T>({ records, withHotkeys = false }: Params<T>) {
  const [pageNumber, setPageNumber] = useState(1);
  const [pageSize, setPageSizeState] = useState(10);
  const [pageRecords, setPageRecordsState] = useState<T[]>(records.slice(0, pageSize));

  function setPageRecords() {
    const startIndex = (pageNumber - 1) * pageSize;
    setPageRecordsState(records.slice(startIndex, startIndex + pageSize));
  }

  const nPages = Math.ceil(records.length / pageSize);
  const hotkeyItems: HotkeyItem[] = [
    ['ArrowLeft', () => setPageNumber(prev => Math.max(prev - 1, 1))],
    ['ArrowRight', () => setPageNumber(prev => Math.min(prev + 1, nPages))],
  ];
  useHotkeys(withHotkeys ? hotkeyItems : []);

  useEffect(() => {
    setPageRecords();
  }, [pageNumber, pageSize, records]);

  function setPageSize(newPageSize: number) {
    setPageSizeState(newPageSize);
    setPageNumber(1);
    setPageRecords();
  }

  return { pageNumber, setPageNumber, pageSize, setPageSize, pageRecords };
}
