import React from "react";
import { Button } from "@/components/ui/button";
import { Play } from "lucide-react";

export interface FindResultClip {
  id: string;
  videoUrl: string;
  thumbnailUrl?: string;
  start: number;
  end: number;
  transcript: string;
}

interface FindResultsProps {
  results: FindResultClip[];
  onPlay: (clip: FindResultClip) => void;
  onDownload: (clip: FindResultClip) => void;
}

const formatTimestamp = (seconds: number) => {
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = Math.floor(seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
};

const FindResults: React.FC<FindResultsProps> = ({ results, onPlay, onDownload }) => {
  if (!results.length) {
    return <div className="text-center text-muted-foreground py-12 text-lg font-medium">No matching clips found.</div>;
  }
  return (
    <div className="space-y-8 w-full">
      {results.map((clip) => (
        <div key={clip.id} className="flex flex-col sm:flex-row items-center gap-6 p-6 bg-card rounded-2xl shadow-xl border border-muted-foreground/10 transition-all hover:shadow-2xl">
          {clip.thumbnailUrl ? (
            <img
              src={clip.thumbnailUrl}
              alt="Clip thumbnail"
              className="w-full sm:w-64 h-40 object-cover rounded-lg shadow-md bg-black"
            />
          ) : (
            <video src={clip.videoUrl} controls className="w-full sm:w-64 h-40 rounded-lg shadow-md bg-black" />
          )}
          <div className="flex-1 w-full">
            <div className="font-bold text-xl mb-2 text-primary">{formatTimestamp(clip.start)} - {formatTimestamp(clip.end)}</div>
            <div className="text-base text-muted-foreground line-clamp-2 mb-2">{clip.transcript}</div>
            <div className="flex gap-3 mt-2">
              <Button
                onClick={() => onPlay(clip)}
                variant="default"
                className="text-base px-8 py-3 flex items-center gap-3 rounded-lg shadow-lg font-bold bg-primary text-primary-foreground border-2 border-primary hover:animate-pulse hover:shadow-xl focus:ring-4 focus:ring-primary/40 transition-all"
              >
                <Play className="w-7 h-7 mr-2" />
                Play
              </Button>
              <Button onClick={() => onDownload(clip)} variant="outline" className="text-base px-6 py-2 rounded-lg shadow-sm hover:shadow-md">
                Download
              </Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default FindResults; 