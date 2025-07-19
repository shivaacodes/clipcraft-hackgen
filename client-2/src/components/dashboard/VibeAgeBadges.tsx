import { Wand2, Users } from "lucide-react";
import React from "react";

interface VibeAgeBadgesProps {
  selectedVibe: string;
  selectedAgeGroup: string;
  vibeColors: Record<string, { bg: string; text: string; border: string }>;
  ageGroupColors: Record<string, { bg: string; text: string; border: string }>;
  ageGroups: { label: string; value: string }[];
}

export default function VibeAgeBadges({ selectedVibe, selectedAgeGroup, vibeColors, ageGroupColors, ageGroups }: VibeAgeBadgesProps) {
  if (!selectedVibe && !selectedAgeGroup) return null;
  // Add color map for vibes
  const vibeColorMap: Record<string, { bg: string; text: string; border: string }> = {
    romantic: { bg: 'bg-pink-50 dark:bg-pink-900/20', text: 'text-pink-700 dark:text-pink-200', border: 'border-pink-500' },
    funny: { bg: 'bg-yellow-50 dark:bg-yellow-900/20', text: 'text-yellow-700 dark:text-yellow-200', border: 'border-yellow-400' },
    thriller: { bg: 'bg-blue-50 dark:bg-blue-900/20', text: 'text-blue-700 dark:text-blue-200', border: 'border-blue-500' },
    heartbreak: { bg: 'bg-rose-50 dark:bg-rose-900/20', text: 'text-rose-700 dark:text-rose-200', border: 'border-rose-500' },
  };
  return (
    <div className="flex gap-4 items-center mb-8 animate-fade-in">
      {selectedVibe && (
        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-full border shadow-sm ${
            vibeColorMap[selectedVibe]
              ? `${vibeColorMap[selectedVibe].bg} ${vibeColorMap[selectedVibe].border}`
              : vibeColors[selectedVibe]?.bg || "bg-primary/10" + " " + (vibeColors[selectedVibe]?.border || "border-primary/20")
          }`}
        >
          <Wand2 className={`w-4 h-4 ${
            vibeColorMap[selectedVibe]
              ? vibeColorMap[selectedVibe].text
              : vibeColors[selectedVibe]?.text || "text-primary"
          }`} />
          <span className={`${
            vibeColorMap[selectedVibe]
              ? vibeColorMap[selectedVibe].text
              : vibeColors[selectedVibe]?.text || "text-primary"
          } font-medium text-sm`}>
            {selectedVibe}
          </span>
        </div>
      )}
      {selectedAgeGroup && (
        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-full border shadow-sm ${
            ageGroupColors[selectedAgeGroup]?.bg || "bg-green-100/30"
          } ${ageGroupColors[selectedAgeGroup]?.border || "border-green-300/30"}`}
        >
          <Users className={`w-4 h-4 ${ageGroupColors[selectedAgeGroup]?.text || "text-green-600"}`} />
          <span className={`${ageGroupColors[selectedAgeGroup]?.text || "text-green-700"} font-medium text-sm capitalize`}>
            {ageGroups.find((a) => a.value === selectedAgeGroup)?.label || selectedAgeGroup}
          </span>
        </div>
      )}
    </div>
  );
} 