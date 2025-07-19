import React, { useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";

export type AudioItem = {
  id: string;
  label: string;
  type: "bgm" | "effect";
  start?: number; // seconds
  duration?: number; // seconds
};

type PositionedAudioItem = AudioItem & { position: number };

interface AudioTrackProps {
  audioItems: AudioItem[];
  onDropAudio: (item: AudioItem) => void;
  onRemoveAudio: (id: string) => void;
  showTimelineLine?: boolean;
  videoDuration?: number; // total video duration in seconds
  onBgmChange?: (start: number, duration: number) => void;
}

export default function AudioTrack({
  audioItems,
  onDropAudio,
  onRemoveAudio,
  showTimelineLine = false,
  videoDuration = 30, // default 30s
  onBgmChange,
}: AudioTrackProps) {
  // Dummy position state: map id to position (px)
  const [positions, setPositions] = useState<{ [id: string]: number }>(() => {
    // Initial positions spaced out
    const spacing = 190;
    const map: { [id: string]: number } = {};
    audioItems.forEach((item, i) => {
      map[item.id] = i * spacing;
    });
    return map;
  });

  const timelineWidth = 600; // px
  const pxPerSec = timelineWidth / videoDuration;
  // Find BGM item
  const bgm = audioItems.find(a => a.type === 'bgm');
  const bgmStart = bgm?.start ?? 0;
  const bgmDuration = bgm?.duration ?? videoDuration;
  // Drag/resize state
  const [bgmDragging, setBgmDragging] = useState(false);
  const [bgmResizing, setBgmResizing] = useState(false);
  const [dragOffset, setDragOffset] = useState(0);

  // Drag logic
  const onBgmDragStart = (e: React.MouseEvent) => {
    setBgmDragging(true);
    setDragOffset(e.clientX - (bgmStart * pxPerSec));
    e.stopPropagation();
  };
  const onBgmDrag = (e: MouseEvent) => {
    if (!bgmDragging) return;
    let newStart = (e.clientX - dragOffset) / pxPerSec;
    newStart = Math.max(0, Math.min(videoDuration - bgmDuration, newStart));
    if (onBgmChange) onBgmChange(newStart, bgmDuration);
  };
  const onBgmDragEnd = () => setBgmDragging(false);

  // Resize logic
  const onBgmResizeStart = (e: React.MouseEvent) => {
    setBgmResizing(true);
    e.stopPropagation();
  };
  const onBgmResize = (e: MouseEvent) => {
    if (!bgmResizing) return;
    const timelineRect = timelineRef.current?.getBoundingClientRect();
    if (!timelineRect) return;
    let mouseX = e.clientX - timelineRect.left;
    let newDuration = mouseX / pxPerSec - bgmStart;
    newDuration = Math.max(1, Math.min(videoDuration - bgmStart, newDuration));
    if (onBgmChange) onBgmChange(bgmStart, newDuration);
  };
  const onBgmResizeEnd = () => setBgmResizing(false);

  // Mouse event listeners for drag/resize
  React.useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (bgmDragging) onBgmDrag(e);
      if (bgmResizing) onBgmResize(e);
    };
    const handleMouseUp = () => {
      if (bgmDragging) onBgmDragEnd();
      if (bgmResizing) onBgmResizeEnd();
    };
    if (bgmDragging || bgmResizing) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [bgmDragging, bgmResizing]);

  const timelineRef = useRef<HTMLDivElement>(null);
  const draggingId = useRef<string | null>(null);
  const dragStartX = useRef<number>(0);
  const dragStartPos = useRef<number>(0);

  const handleDragStart = (e: React.DragEvent, id: string) => {
    draggingId.current = id;
    dragStartX.current = e.clientX;
    dragStartPos.current = positions[id] || 0;
  };

  const handleDrag = (e: React.DragEvent) => {
    if (!draggingId.current) return;
    const dx = e.clientX - dragStartX.current;
    setPositions(prev => ({
      ...prev,
      [draggingId.current!]: Math.max(0, Math.min((timelineRef.current?.offsetWidth || 600) - 180, dragStartPos.current + dx)),
    }));
  };

  const handleDragEnd = () => {
    draggingId.current = null;
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const data = e.dataTransfer.getData("audio-item");
    if (data) {
      const item: AudioItem = JSON.parse(data);
      onDropAudio(item);
    }
  };

  return (
    <div className="mt-8 mb-4">
      <div
        ref={timelineRef}
        className="relative w-full min-h-[60px] bg-background dark:bg-zinc-900 rounded-lg flex items-center px-4 py-3 border-2 border-dashed border-indigo-400/40 dark:border-indigo-500/60 overflow-x-auto"
        style={{ minWidth: 0, height: 70 }}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {/* Timeline bar (optional) */}
        {showTimelineLine && (
          <div className="absolute left-0 right-0 top-1/2 h-1 bg-indigo-200 dark:bg-indigo-700/40" style={{ transform: "translateY(-50%)" }} />
        )}
        {/* BGM Timeline Bar (UI unchanged, logic updated) */}
        {bgm && (
          <div
            className="flex items-center gap-2 bg-primary/10 border border-indigo-400/40 rounded-md px-3 py-1 text-sm font-medium text-indigo-900 dark:text-white absolute"
            style={{
              left: bgmStart * pxPerSec,
              width: bgmDuration * pxPerSec,
              top: 10, // BGM at top
              height: 30,
              cursor: bgmDragging ? 'grabbing' : 'grab',
              zIndex: 20,
              minWidth: 60,
            }}
            onMouseDown={onBgmDragStart}
          >
            <span className="max-w-[140px] whitespace-nowrap overflow-hidden text-ellipsis">{bgm.label}</span>
            <Button size="sm" variant="ghost" onClick={() => onRemoveAudio(bgm.id)} className="w-6 h-6 p-0 ml-auto" aria-label="Remove audio">
              <Trash2 className="w-3 h-3" />
            </Button>
            <div
              style={{
                position: 'absolute',
                right: 0,
                width: 18,
                height: 30,
                background: 'rgba(0,0,0,0.12)',
                cursor: 'ew-resize',
                borderTopRightRadius: 6,
                borderBottomRightRadius: 6,
                zIndex: 30,
                transition: 'background 0.2s',
              }}
              className="hover:bg-indigo-300/40"
              onMouseDown={onBgmResizeStart}
            />
          </div>
        )}
        {/* Placeholder text only if no BGM and no effects */}
        {audioItems.filter(a => a.type === 'effect').length === 0 && !bgm && (
          <span
            className="text-muted-foreground text-sm z-10 absolute w-full flex items-center justify-center"
            style={{ left: 0, top: 0, height: '100%' }}
          >
            Drag BGM or sound effects here
          </span>
        )}
        {/* Other audio items (effects) */}
        {audioItems.filter(a => a.type === 'effect').map((item, i) => {
          const isEffect = item.type === "effect";
          return (
            <div
              key={item.id}
              className="absolute z-10 flex items-center gap-2 px-3 py-1 text-sm font-medium shadow cursor-grab select-none rounded-md bg-yellow-100 dark:bg-yellow-300/20 border border-yellow-400/60 dark:border-yellow-300/60 text-yellow-900 dark:text-yellow-200"
              style={{ left: (item.start ?? 0) * pxPerSec, top: 45, width: 180, minWidth: 180, paddingRight: 8 }}
              draggable
              onDragStart={e => handleDragStart(e, item.id)}
              onDrag={handleDrag}
              onDragEnd={handleDragEnd}
            >
              <span className="max-w-[140px] whitespace-nowrap overflow-hidden text-ellipsis">{item.label}</span>
              <Button size="sm" variant="ghost" onClick={() => onRemoveAudio(item.id)} className="w-6 h-6 p-0 ml-auto" aria-label="Remove audio">
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          );
        })}
      </div>
    </div>
  );
} 