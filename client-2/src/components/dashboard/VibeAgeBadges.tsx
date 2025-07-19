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
  return (
    <div className="flex gap-4 items-center mb-8 animate-fade-in">
      {selectedVibe && (
        <div
          className={`flex items-center gap-2 px-4 py-2 rounded-full border shadow-sm ${
            vibeColors[selectedVibe]?.bg || "bg-primary/10"
          } ${vibeColors[selectedVibe]?.border || "border-primary/20"}`}
        >
          <Wand2 className={`w-4 h-4 ${vibeColors[selectedVibe]?.text || "text-primary"}`} />
          <span className={`${vibeColors[selectedVibe]?.text || "text-primary"} font-medium text-sm`}>
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