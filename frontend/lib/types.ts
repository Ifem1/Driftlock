export type BaselineReview = {
  status?: "BASELINE_VERIFIED" | "PROMISE_NOT_SUPPORTED" | "SOURCE_UNAVAILABLE" | "AMBIGUOUS" | string;
  baseline_compliant?: boolean;
  breach_condition_present?: boolean;
  basis?: string;
  recorded_at?: string;
  [key: string]: unknown;
};

export type InspectionReview = {
  status?: "NO_RELEVANT_CHANGE" | "MATERIAL_CHANGE" | "SOURCE_UNAVAILABLE" | "AMBIGUOUS" | string;
  current_compliant?: boolean;
  breach_condition_now_supported?: boolean;
  promise_still_supported?: boolean;
  basis?: string;
  recorded_at?: string;
  [key: string]: unknown;
};

export type Covenant = {
  id: string;
  title: string;
  subject: string;
  canonical_url: string;
  protected_promise: string;
  breach_rule?: string;
  permitted_changes?: string;
  owner: string;
  beneficiary: string;
  finder_reward_bps: string;
  stake_atto: string;
  remaining_stake_atto: string;
  challenge_bond_atto: string;
  status: string;
  created_at: string;
  activated_at: string;
  expires_at: string;
  baseline_deadline?: string;
  baseline_review?: BaselineReview | null;
  pending_challenge?: string;
  challenge_count: number | string;
  last_challenge_at?: string;
  last_inspection?: InspectionReview | null;
  breach_challenge?: string;
  breached_at?: string;
  closed_at?: string;
  can_challenge?: boolean;
  can_expire?: boolean;
  can_expire_baseline?: boolean;
};

export type Challenge = {
  id: string;
  covenant_id: string;
  challenger: string;
  status: string;
  bond_atto: string;
  created_at: string;
  stage_deadline: string;
  inspection?: InspectionReview | null;
  judgment?: Record<string, unknown> | null;
  settled_at?: string;
  finder_reward_atto?: string;
  can_expire?: boolean;
};

export type ProtocolStats = {
  product: string;
  version: string;
  network: string;
  chain_id: string;
  rpc: string;
  inspector: string;
  judge: string;
  components_configured: boolean;
  admin_controls: boolean;
  protocol_fee_bps: string;
  max_challenges_per_covenant: string;
  total_covenants: string;
  total_challenges: string;
  covenants_activated: string;
  covenants_breached: string;
  covenants_expired: string;
  accounting_balanced: boolean;
};
