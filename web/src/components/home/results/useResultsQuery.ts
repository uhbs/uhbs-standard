import { useEffect, useMemo, useState } from "react";
import { LAB_RESULTS } from "../../../data/labResults";
import type { LabResult } from "../../../data/labResults";

export type SortKey = "uhqsQuick" | "uhqsFull";
export type SortDir = "asc" | "desc";
export type ViewMode = "cards" | "list";

export function useResultsQuery() {
  const [protocolFilter, setProtocolFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<ViewMode>("cards");
  const [page, setPage] = useState(0);
  const [sortKey, setSortKey] = useState<SortKey | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>("desc");
  const pageSize = viewMode === "cards" ? 3 : 12;

  const filteredLabs = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    let base: LabResult[] =
      protocolFilter === "all"
        ? LAB_RESULTS
        : LAB_RESULTS.filter((lab) => lab.protocol === protocolFilter);
    if (q) {
      base = base.filter(
        (lab) =>
          lab.name.toLowerCase().includes(q) ||
          lab.repo.toLowerCase().includes(q) ||
          lab.protocolLabel.toLowerCase().includes(q) ||
          lab.classLabel.toLowerCase().includes(q),
      );
    }
    if (!sortKey) return base;
    return [...base].sort((a, b) => {
      const av = a[sortKey] ?? -1;
      const bv = b[sortKey] ?? -1;
      return sortDir === "asc" ? av - bv : bv - av;
    });
  }, [protocolFilter, searchQuery, sortKey, sortDir]);

  const pageCount = Math.max(1, Math.ceil(filteredLabs.length / pageSize));
  const safePage = Math.min(page, pageCount - 1);
  const pageLabs = filteredLabs.slice(safePage * pageSize, (safePage + 1) * pageSize);

  useEffect(() => {
    if (page !== safePage) setPage(safePage);
  }, [page, safePage]);

  const setFilter = (id: string) => {
    setProtocolFilter(id);
    setPage(0);
  };

  const toggleSort = (key: SortKey) => {
    if (sortKey !== key) {
      setSortKey(key);
      setSortDir("desc");
    } else if (sortDir === "desc") {
      setSortDir("asc");
    } else {
      setSortKey(null);
      setSortDir("desc");
    }
  };

  return {
    protocolFilter,
    searchQuery,
    setSearchQuery,
    viewMode,
    setViewMode,
    page,
    setPage,
    sortKey,
    sortDir,
    pageSize,
    filteredLabs,
    pageCount,
    safePage,
    pageLabs,
    setFilter,
    toggleSort,
  };
}
