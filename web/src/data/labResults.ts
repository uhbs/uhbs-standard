/** Published UHBS lab results shown on the landing hub Results section. */

import labResultsJson from "./labResults.json";
import protocolFiltersJson from "./protocolFilters.json";

export type LabResult = {
  name: string;
  classLabel: string;
  protocol: string;
  protocolLabel: string;
  repo: string;
  /** GitHub `pushed_at` date (YYYY-MM-DD) for the upstream repo */
  repoUpdated: string;
  uhqsQuick: number | null;
  uhqsFull: number | null;
  gradeQuick: string;
  gradeFull: string;
  hub: string;
  tutorial: string;
  methodology: string;
  scorecard: string;
  quick: string;
  full: string;
  quickCard: string;
  fullCard: string;
};

export type ProtocolFilter = {
  id: string;
  label: string;
};

export const PROTOCOL_FILTERS = protocolFiltersJson as ProtocolFilter[];
export const LAB_RESULTS = labResultsJson as LabResult[];
