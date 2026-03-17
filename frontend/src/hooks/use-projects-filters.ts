import { useState, useEffect, useMemo, useCallback, useRef } from "react";
import { useSearchParams } from "react-router-dom";

export interface ProjectsFilters {
  search: string;
  state: string;
  ownership: string;
}

const DEBOUNCE_MS = 300;

export function useProjectsFilters() {
  const [searchParams, setSearchParams] = useSearchParams();
  const searchParamsRef = useRef(searchParams);
  searchParamsRef.current = searchParams;
  const setSearchParamsRef = useRef(setSearchParams);
  setSearchParamsRef.current = setSearchParams;

  const urlSearch = searchParams.get("search") ?? "";
  const urlState = searchParams.get("state") ?? "";
  const urlOwnership = searchParams.get("filter") ?? "";

  const [searchInput, setSearchInput] = useState(urlSearch);
  const [debouncedSearch, setDebouncedSearch] = useState(urlSearch);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput);
      const params = new URLSearchParams(searchParamsRef.current);
      if (searchInput) {
        params.set("search", searchInput);
      } else {
        params.delete("search");
      }
      setSearchParamsRef.current(params, { replace: true });
    }, DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const filters: ProjectsFilters = useMemo(
    () => ({
      search: debouncedSearch,
      state: urlState,
      ownership: urlOwnership,
    }),
    [debouncedSearch, urlState, urlOwnership],
  );

  const setStateFilter = useCallback((value: string) => {
    const params = new URLSearchParams(searchParamsRef.current);
    if (value) {
      params.set("state", value);
    } else {
      params.delete("state");
    }
    setSearchParamsRef.current(params, { replace: true });
  }, []);

  const setOwnershipFilter = useCallback((value: string) => {
    const params = new URLSearchParams(searchParamsRef.current);
    if (value) {
      params.set("filter", value);
    } else {
      params.delete("filter");
    }
    setSearchParamsRef.current(params, { replace: true });
  }, []);

  const clearFilters = useCallback(() => {
    setSearchInput("");
    setDebouncedSearch("");
    setSearchParamsRef.current({}, { replace: true });
  }, []);

  const hasActiveFilters = !!(debouncedSearch || urlState || urlOwnership);

  return {
    filters,
    searchInput,
    setSearchInput,
    setStateFilter,
    setOwnershipFilter,
    clearFilters,
    hasActiveFilters,
  };
}
