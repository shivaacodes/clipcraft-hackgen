import React from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger, DropdownMenuRadioGroup, DropdownMenuRadioItem, DropdownMenuLabel, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { Upload, Scissors, Users, ChevronDown } from "lucide-react";

interface TopActionRowProps {
  fileInputRef: React.RefObject<HTMLInputElement>;
  handleVideoSelect: (event: React.ChangeEvent<HTMLInputElement>) => void;
  handleImportClick: () => void;
  open: boolean;
  setOpen: (open: boolean) => void;
  selectedVibe: string;
  setSelectedVibe: (vibe: string) => void;
  vibes: { label: string; value: string }[];
  vibeColors: Record<string, { bg: string; text: string; border: string }>;
  selectedAgeGroup: string;
  setSelectedAgeGroup: (age: string) => void;
  ageGroups: { label: string; value: string }[];
  addSubtitles: boolean;
  setAddSubtitles: (v: boolean) => void;
}

export default function TopActionRow({
  fileInputRef,
  handleVideoSelect,
  handleImportClick,
  open,
  setOpen,
  selectedVibe,
  setSelectedVibe,
  vibes,
  vibeColors,
  selectedAgeGroup,
  setSelectedAgeGroup,
  ageGroups,
  addSubtitles,
  setAddSubtitles,
}: TopActionRowProps) {
  return (
    <div className="flex items-start gap-4 flex-wrap">
      {/* Import + Editor */}
      <div className="flex gap-2">
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleVideoSelect}
          className="hidden"
        />
        <Button variant="outline" onClick={handleImportClick}>
          <Upload className="w-4 h-4 mr-2" />
          Import Video
        </Button>

        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button variant="outline">
              <Scissors className="w-4 h-4 mr-2" />
              Editor Options
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle className="text-xl font-semibold">Choose Your Vibe</DialogTitle>
              <p className="text-sm text-muted-foreground">Select one vibe for your video</p>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <div className="grid grid-cols-3 gap-4">
                  {vibes.map((v) => {
                    const isSelected = selectedVibe === v.value;
                    const color = vibeColors[v.value] || { bg: "bg-primary/10", text: "text-primary", border: "border-primary/20" };
                    return (
                      <div key={v.value} className="flex flex-col items-center gap-2">
                        <button
                          onClick={() => {
                            setSelectedVibe(isSelected ? "" : v.value);
                          }}
                          className={`relative w-16 h-16 text-3xl flex items-center justify-center rounded-full border-2 transition-all duration-200 ${
                            isSelected
                              ? `${color.border} ${color.bg} shadow-lg scale-110`
                              : "border-muted hover:border-muted-foreground/50 hover:bg-muted/50 hover:scale-105"
                          }`}
                        >
                          <span className={color.text}>{v.label}</span>
                          {isSelected && (
                            <div className="absolute -top-1 -right-1 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                              <span className="text-sm text-primary-foreground">✓</span>
                            </div>
                          )}
                        </button>
                        <span className="text-sm text-muted-foreground font-medium capitalize">{v.value}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
              <div className="pt-2 flex justify-between items-center">
                <div className="text-sm text-muted-foreground">
                  {selectedVibe ? `${selectedVibe} vibe selected` : 'No vibe selected'}
                </div>
                <Button onClick={() => setOpen(false)}>Done</Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline">
              <Users className="w-4 h-4 mr-2" />
              Age Group
              <ChevronDown className="w-4 h-4 ml-2" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className="w-56">
            <DropdownMenuLabel>Target Age Group</DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuRadioGroup value={selectedAgeGroup} onValueChange={setSelectedAgeGroup}>
              {ageGroups.map((group) => (
                <DropdownMenuRadioItem key={group.value} value={group.value}>
                  {group.label}
                </DropdownMenuRadioItem>
              ))}
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Find button replaces subtitle toggle */}
        <div className="flex items-center ml-4">
          <a href="/find">
            <Button
              type="button"
              className="bg-black text-white dark:bg-white dark:text-black hover:opacity-90 transition-colors px-6 py-2 font-semibold shadow"
            >
              Find
            </Button>
          </a>
        </div>
      </div>
      {/* Export button removed from top action row */}
    </div>
  );
} 