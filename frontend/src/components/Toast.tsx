import React from "react";

interface ToastProps {
  show: boolean;
  title: string;
  subtitle: string;
}

export const Toast: React.FC<ToastProps> = ({ show, title, subtitle }) => {
  if (!show) return null;

  return (
    <div
      className="fixed bottom-6 right-6 z-50 bg-secondary-container text-on-secondary-container px-space-xl py-space-md rounded-lg shadow-2xl flex items-center gap-space-md transition-all duration-300"
      id="action-toast"
    >
      <span className="material-symbols-outlined text-tertiary text-[22px]">check_circle</span>
      <div className="flex flex-col">
        <span className="font-headline-sm text-headline-sm font-bold text-on-surface">{title}</span>
        <span className="font-body-xs text-body-xs text-on-surface-variant">{subtitle}</span>
      </div>
    </div>
  );
};
