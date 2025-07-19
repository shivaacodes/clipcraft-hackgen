import React, { useRef, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose,
} from "@/components/ui/dialog";
import { Film, Music, Waves, Zap, Upload } from "lucide-react";

const GENRES = [
  { name: "Cinematic", gradient: "bg-gradient-to-r from-purple-500 via-indigo-500 to-blue-500", icon: Film, file: "/assets/bgm/cinematic.mp3" },
  { name: "Upbeat", gradient: "bg-gradient-to-r from-pink-500 via-red-400 to-yellow-300", icon: Music, file: "/assets/bgm/upbeat.mp3" },
  { name: "Ambient", gradient: "bg-gradient-to-r from-blue-400 via-cyan-400 to-green-300", icon: Waves, file: "/assets/bgm/ambient.mp3" },
  { name: "Dramatic", gradient: "bg-gradient-to-r from-yellow-400 via-orange-500 to-red-500", icon: Zap, file: "/assets/bgm/dramatic.mp3" },
];

export default function BgmDialog({ open, onOpenChange, onSelect }: { open: boolean; onOpenChange: (open: boolean) => void; onSelect?: (item: { id: string; label: string; type: "bgm"; filename: string }) => void }) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playingIdx, setPlayingIdx] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);

  const handlePlay = (idx: number) => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
    }
    const audio = new Audio(GENRES[idx].file);
    audioRef.current = audio;
    setPlayingIdx(idx);
    audio.play();
    audio.onended = () => setPlayingIdx(null);
  };

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch("/api/upload-bgm", {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      onSelect && onSelect({ id: 'bgm-imported', label: file.name, type: 'bgm', filename: data.filename });
      onOpenChange(false);
    } catch (err) {
      alert("Failed to upload BGM. Please try again.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent showCloseButton>
        <DialogHeader>
          <DialogTitle>Select a BGM Genre</DialogTitle>
        </DialogHeader>
        <div className="flex flex-col gap-4 mt-4">
          {GENRES.map((genre, idx) => {
            const Icon = genre.icon;
            return (
              <div
                key={genre.name}
                className={`rounded-lg h-16 flex items-center px-6 text-lg font-semibold text-white shadow transition-all duration-200 ${genre.gradient} cursor-pointer`}
                style={{ boxShadow: '0 4px 24px 0 rgba(0,0,0,0.10)' }}
                onClick={() => handlePlay(idx)}
              >
                <Icon className="w-6 h-6 mr-3 opacity-90" />
                <span className="flex-1">{genre.name}</span>
                <button
                  className="ml-4 px-3 py-1 text-xs rounded bg-white/20 hover:bg-white/40 text-white border border-white/30"
                  onClick={e => {
                    e.stopPropagation();
                    onSelect && onSelect({ id: 'bgm-' + genre.name, label: genre.name, type: 'bgm', filename: genre.file.split('/').pop() || '' });
                  }}
                >
                  Select
                </button>
              </div>
            );
          })}
          {/* Import BGM option */}
          <div className="flex items-center gap-3 mt-2">
            <button
              className="flex items-center gap-1 px-2 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs disabled:opacity-60 border border-indigo-700"
              onClick={handleImportClick}
              disabled={uploading}
            >
              <Upload className="w-4 h-4" />
              {uploading ? "Uploading..." : "Import BGM from device"}
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="audio/*"
              className="hidden"
              onChange={handleFileChange}
              disabled={uploading}
            />
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
} 