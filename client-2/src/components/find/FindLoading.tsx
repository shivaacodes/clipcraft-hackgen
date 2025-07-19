import React from "react";

const FindLoading: React.FC<{ message?: string }> = ({ message }) => {
  return (
    <div className="flex flex-col items-center justify-center py-16 w-full">
      <div className="animate-spin rounded-full h-14 w-14 border-t-4 border-b-4 border-primary mb-6" />
      <div className="text-muted-foreground text-lg font-medium">{message || "Processing..."}</div>
    </div>
  );
};

export default FindLoading; 