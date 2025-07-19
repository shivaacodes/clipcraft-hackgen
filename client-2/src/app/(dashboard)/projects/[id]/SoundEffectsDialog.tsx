import React, { useRef, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog";

const EFFECTS = [
  { emoji: "🔊", file: "/assets/effects/effect-1.mp3" },
  { emoji: "🔊", file: "/assets/effects/effect-2.mp3" },
  { emoji: "🔊", file: "/assets/effects/effect-3.mp3" },
];

export default function SoundEffectsDialog({ open, onOpenChange, onSelect }: { open: boolean; onOpenChange: (open: boolean) => void; onSelect?: (item: { id: string; label: string; type: "effect" }) => void }) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playingIdx, setPlayingIdx] = useState<number | null>(null);

  const handlePlay = (idx: number) => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    const audio = new Audio(EFFECTS[idx].file);
    audioRef.current = audio;
    setPlayingIdx(idx);
    audio.play();
    audio.onended = () => setPlayingIdx(null);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent showCloseButton>
        <DialogHeader>
          <DialogTitle>Select a Sound Effect</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-4 mt-4">
          {EFFECTS.map((effect, idx) => (
            <div key={idx}>
              <div
                className={`rounded-lg h-20 flex items-center justify-center text-3xl bg-gray-900 select-none transition-all duration-200 cursor-pointer`}
                onClick={() => handlePlay(idx)}
              >
                <span className="flex-1 text-center">{effect.emoji}</span>
                <button
                  className="ml-4 mr-4 px-3 py-1 text-xs rounded bg-white/20 hover:bg-white/40 text-white border border-white/30"
                  onClick={e => {
                    e.stopPropagation();
                    onSelect && onSelect({ id: 'effect-' + idx, label: effect.emoji, type: 'effect' });
                  }}
                >
                  Select
                </button>
              </div>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  );
} 