import { ReactNode } from 'react';
import { T } from '../../lib/tokens';

interface CardProps {
  children?: ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
}

export function Card({ children, className = '', title, subtitle }: CardProps) {
  if (title !== undefined || subtitle !== undefined) {
    return (
      <div className={`${T.card} ${T.ring} ring-1 rounded-lg p-4 ${className}`}>
        {title && <h3 className="text-lg font-semibold">{title}</h3>}
        {subtitle && <p className="text-slate-300 text-sm">{subtitle}</p>}
        {children}
      </div>
    );
  }

  return (
    <div className={`${T.card} ${T.ring} ring-1 rounded-lg p-4 ${className}`}>
      {children}
    </div>
  );
}