import React from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger, DropdownMenuRadioGroup, DropdownMenuRadioItem, DropdownMenuLabel, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { Upload, Scissors, Users, ChevronDown } from "lucide-react";
import { motion } from "framer-motion";

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
            {/* --- Custom Vibe Cards --- */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-8 mt-8">
              {[
                {
                  key: "romantic",
                  emoji: "💖",
                  title: "Lovely-Dovey",
                  description: "All the feels! Sweet, romantic, and heart-melting moments that make you believe in love.",
                  image: "/assets/bg/lovely-dovey.jpeg",
                },
                {
                  key: "funny",
                  emoji: "🤣",
                  title: "LOL Moments",
                  description: "Get ready to giggle! Outrageous, silly, and laugh-out-loud scenes for instant mood-lift.",
                  image: "/assets/bg/lol-moments.jpeg",
                },
                {
                  key: "thriller",
                  emoji: "😱",
                  title: "Edge of Your Seat",
                  description: "Hold your breath! Suspenseful, intense, and jaw-dropping moments that keep you guessing.",
                  image: "/assets/bg/edge-of-seat.jpeg",
                },
                {
                  key: "heartbreak",
                  emoji: "💔😭",
                  title: "Tearjerker",
                  description: "Grab the tissues! Emotional, powerful, and soul-stirring scenes that tug at your heartstrings.",
                  image: "/assets/bg/heartbreak.jpeg",
                },
              ].map((vibe) => {
                const isSelected = selectedVibe === vibe.key;
                return (
                  <motion.div
                    key={vibe.key}
                    whileHover={{ scale: 1.025, boxShadow: "0 4px 24px 0 rgba(0,0,0,0.10)" }}
                    transition={{ type: "spring", stiffness: 250, damping: 22 }}
                    className={`relative bg-background border shadow-sm overflow-hidden group transition-all duration-300 min-h-[250px] flex flex-col justify-between cursor-pointer 
                      ${isSelected ? 'border-primary/80 border-2' : 'border-[#2d2d2f] border'} 
                      ${!isSelected && 'hover:border-primary/60'}`}
                    onClick={() => {
                      setSelectedVibe(isSelected ? "" : vibe.key);
                      setOpen(false);
                    }}
                  >
                    <div className="w-full h-40 bg-cover bg-center" style={{ backgroundImage: `url(${vibe.image})` }} />
                    <div className="p-5 flex flex-col gap-3 flex-1">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-2xl md:text-3xl mr-2 select-none" aria-label={vibe.title}>{vibe.emoji}</span>
                        <h3 className="font-semibold text-lg tracking-tight text-zinc-900 dark:text-zinc-100 flex-1">{vibe.title}</h3>
                      </div>
                      {/* Description only in overlay below */}
                      {/* <p className="text-sm text-muted-foreground leading-snug">{vibe.description}</p> */}
                      <motion.div
                        initial={{ opacity: 0, y: 24 }}
                        whileHover={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 24 }}
                        transition={{ duration: 0.55, ease: "easeInOut" }}
                        className="absolute left-0 right-0 bottom-0 p-5 bg-black/80 text-base text-white opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto z-10 shadow-xl backdrop-blur-md"
                      >
                        {vibe.description}
                      </motion.div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
            {/* --- End Custom Vibe Cards --- */}
            {/* <div className="space-y-4"> ...old vibe grid... </div> */}
            {/* <div className="pt-2 flex justify-between items-center"> ...old footer... </div> */}
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