"use client";

import React, { useRef, useState } from "react";
import FindInput from "@/components/find/FindInput";
import FindResults, { FindResultClip } from "@/components/find/FindResults";
import DashboardLoading from "@/app/(dashboard)/dashboard/loading";
import { Button } from "@/components/ui/button";
import { Upload } from "lucide-react";
import { Eye } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogClose } from "@/components/ui/dialog";

// Use NEXT_PUBLIC_BACKEND_URL from .env.local, fallback to localhost
const API_URL = process.env.NEXT_PUBLIC_BACKEND_URL
  ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1/find/find`
  : "http://localhost:8000/api/v1/find/find";

const FindPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<FindResultClip[]>([]);
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [modalClip, setModalClip] = useState<FindResultClip | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleVideoSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedVideo(file);
      setResults([]);
      setError(null);
    }
  };

  const handleSubmit = async (input: string, isVoice: boolean, language: string) => {
    if (!selectedVideo) {
      setError("Please import a video first.");
      return;
    }
    setLoading(true);
    setResults([]);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("video", selectedVideo);
      formData.append("query", input);
      formData.append("language", language); // Pass language to backend
      const res = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const errText = await res.text();
        setError(`Error ${res.status}: ${errText}`);
        console.error("Find API error:", res.status, errText);
        return;
      }
      const data = await res.json();
      setResults(
        (data.results || []).map((clip: any, idx: number) => {
          const backendBase = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
          const makeAbsolute = (url: string | undefined) => {
            if (!url) return undefined;
            if (url.startsWith("http://") || url.startsWith("https://")) return url;
            return backendBase.replace(/\/$/, "") + (url.startsWith("/") ? url : "/" + url);
          };
          return {
          id: idx.toString(),
            videoUrl: makeAbsolute(clip.video_url),
            thumbnailUrl: makeAbsolute(clip.thumbnail_url),
          start: clip.start,
          end: clip.end,
          transcript: clip.transcript,
          };
        })
      );
    } catch (e: any) {
      setError(e.message || "Unknown error");
      console.error("Find API fetch error:", e);
    } finally {
      setLoading(false);
    }
  };

  const handlePlay = (clip: FindResultClip) => {
    setModalClip(clip);
  };

  const handleDownload = (clip: FindResultClip) => {
    const a = document.createElement("a");
    a.href = clip.videoUrl;
    a.download = `clip-${clip.id}.mp4`;
    a.click();
  };

  return (
    <div className="max-w-3xl mx-auto py-20 px-4 sm:px-8 flex flex-col items-center gap-10">
      <h1 className="text-4xl font-extrabold mb-2 tracking-tight text-center flex items-center justify-center gap-3">
        <span role="img" aria-label="search">🔎</span>
        <Eye className="w-8 h-8 text-primary/80" />
        <span role="img" aria-label="sparkles">✨</span>
        Find a Moment
        <span role="img" aria-label="film">🎬</span>
      </h1>
      <p className="text-lg text-muted-foreground mb-6 text-center max-w-xl">
        <span role="img" aria-label="lightbulb">💡</span> Import a video and <b>describe a scene, quote, or vibe</b> you want to find.<br />
        <span role="img" aria-label="rocket">🚀</span> Our AI will find the best moments for you!
      </p>
      <div className="flex flex-col sm:flex-row items-center gap-4 mb-4 w-full justify-center">
        <input
          ref={fileInputRef}
          type="file"
          accept="video/*"
          onChange={handleVideoSelect}
          className="hidden"
        />
        <Button variant="outline" onClick={handleImportClick} className="text-base px-6 py-3 shadow-md hover:shadow-lg transition-all flex items-center gap-2">
          <Upload className="w-5 h-5 mr-1" />
          <span role="img" aria-label="clapper">🎬</span> Import Video
        </Button>
        {selectedVideo && (
          <span className="ml-0 sm:ml-4 text-base text-muted-foreground font-medium truncate max-w-xs flex items-center gap-2">
            <span role="img" aria-label="paperclip">📎</span> {selectedVideo.name}
          </span>
        )}
      </div>
      <FindInput onSubmit={handleSubmit} isLoading={loading} />
      {error && <div className="text-red-500 py-2 text-lg font-semibold text-center w-full">{error}</div>}
      <div className="w-full">
      {loading ? (
        <DashboardLoading />
      ) : (
        <FindResults results={results} onPlay={handlePlay} onDownload={handleDownload} />
      )}
      </div>
      {/* Modal for video playback */}
      <Dialog open={!!modalClip} onOpenChange={(open) => !open && setModalClip(null)}>
        <DialogContent className="max-w-2xl w-full p-0 overflow-hidden rounded-2xl shadow-2xl" showCloseButton>
          <DialogHeader className="w-full px-6 pt-6 pb-2">
            <DialogTitle className="text-2xl font-bold text-left w-full flex items-center gap-2">
              <span role="img" aria-label="play">▶️</span> Clip Preview
            </DialogTitle>
          </DialogHeader>
          {modalClip && (
            <div className="space-y-6 p-6 w-full">
              <video src={modalClip.videoUrl} controls autoPlay className="w-full h-[360px] sm:h-[420px] rounded-xl bg-black shadow-lg mb-4" />
              <div className="text-lg text-muted-foreground font-medium text-left w-full flex items-center gap-2">
                <span role="img" aria-label="speech">💬</span> {modalClip.transcript}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default FindPage; 