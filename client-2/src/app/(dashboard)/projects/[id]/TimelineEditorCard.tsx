import AudioTrack, { AudioItem } from "./AudioTrack";
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Move, Music, Play, Volume2, Plus } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

interface TimelineEditorCardProps {
  timelineItems: any[];
  setTimelineItems: (items: any[]) => void;
  imageInputRef: React.RefObject<HTMLInputElement>;
  handleDrop: (e: React.DragEvent) => void;
  handleDragOver: (e: React.DragEvent) => void;
  audioItems: AudioItem[];
  setAudioItems: (items: AudioItem[]) => void;
  handleDropAudio: (e: React.DragEvent) => void;
  handleRemoveAudio: (id: string) => void;
  showBgmDialog: boolean;
  setShowBgmDialog: (show: boolean) => void;
  showSoundEffectsDialog: boolean;
  setShowSoundEffectsDialog: (show: boolean) => void;
  BgmDialog: React.ReactNode;
  SoundEffectsDialog: React.ReactNode;
  handleRenderFinalVideo: () => void;
  isRendering: boolean;
  selectedBGM: AudioItem | null;
}

export default function TimelineEditorCard({
  timelineItems,
  setTimelineItems,
  imageInputRef,
  handleDrop,
  handleDragOver,
  audioItems,
  setAudioItems,
  handleDropAudio,
  handleRemoveAudio,
  showBgmDialog,
  setShowBgmDialog,
  showSoundEffectsDialog,
  setShowSoundEffectsDialog,
  BgmDialog,
  SoundEffectsDialog,
  handleRenderFinalVideo,
  isRendering,
  selectedBGM,
}: TimelineEditorCardProps) {
  const [imageUploading, setImageUploading] = useState(false);
  const [imageUploadError, setImageUploadError] = useState<string | null>(null);
  // BGM drag/resize handler
  const handleBgmChange = (start: number, duration: number) => {
    setAudioItems(
      audioItems.map((a: AudioItem) =>
        a.type === 'bgm' ? { ...a, start, duration } : a
      )
    );
  };
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Move className="w-5 h-5" />
          Timeline Editor
          {timelineItems.length > 0 && (
            <Badge variant="secondary">{timelineItems.length}</Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* BGM Controls */}
        <div className="border-b pb-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="flex items-center gap-2 font-medium">
              <Music className="w-4 h-4" />
              Background Music
            </h4>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => setShowBgmDialog(true)}>
                <Plus className="w-3 h-3 mr-1" />
                Add BGM
              </Button>
              <Button variant="outline" size="sm" onClick={() => setShowSoundEffectsDialog(true)}>
                <Volume2 className="w-4 h-4 mr-1" />
                Sound Effects
              </Button>
              {SoundEffectsDialog}
            </div>
            {BgmDialog}
          </div>
        </div>
        {/* Video Timeline */}
        <div>
          <h4 className="flex items-center gap-2 font-medium mb-3">
            <Play className="w-4 h-4" />
            Video Timeline
          </h4>
          {/* ... rest of your timeline UI ... */}
        </div>
        {/* Audio Track UI inside the Timeline Editor card */}
        <AudioTrack
          audioItems={audioItems}
          onDropAudio={handleDropAudio}
          onRemoveAudio={handleRemoveAudio}
          onBgmChange={handleBgmChange}
        />
        {/* Render Button ... */}
      </CardContent>
    </Card>
  );
} 