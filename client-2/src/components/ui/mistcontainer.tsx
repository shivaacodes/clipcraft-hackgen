import React from "react";

export default function MistContainer({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`relative overflow-hidden ${className}`}>
      <div className="absolute inset-0 bg-gradient-to-br from-gray-800/10 to-gray-900/10" />
      {/* content */}
      {children}
    </div>
  );
}
