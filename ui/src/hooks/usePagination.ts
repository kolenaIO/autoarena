import { useEffect, useState } from 'react';

export function usePagination<T>(records: T[]) {
  const [pageNumber, setPageNumber] = useState(1);
  const [pageSize, setPageSizeState] = useState(10);
  const [pageRecords, setPageRecordsState] = useState(records.slice(0, pageSize));

  function setPageRecords() {
    const startIndex = (pageNumber - 1) * pageSize;
    setPageRecordsState(records.slice(startIndex, startIndex + pageSize));
  }

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
