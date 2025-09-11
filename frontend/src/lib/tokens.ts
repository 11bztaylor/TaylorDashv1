/**
 * TaylorDash Design Token System
 * Exact token definitions for consistent theming
 */

export const T = {
  // Background tokens
  bg: 'bg-slate-900',
  
  // Card/surface tokens
  card: 'bg-slate-800',
  
  // Text tokens
  text: 'text-slate-100',
  
  // Ring/focus tokens
  ring: 'ring-slate-600'
} as const;

export type TokenKeys = keyof typeof T;