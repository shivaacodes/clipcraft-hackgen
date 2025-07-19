import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Move, Music, Plus, Volume2, Play, Trash2, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import AudioTrack, { AudioItem } from "../../app/(dashboard)/projects/[id]/AudioTrack";

interface TimelineEditorCardProps {
  timelineItems: any[];
  setTimelineItems: React.Dispatch<React.SetStateAction<any[]>>;
  imageInputRef: React.RefObject<HTMLInputElement>;
  handleDrop: (e: React.DragEvent) => void;
  handleDragOver: (e: React.DragEvent) => void;
  audioItems: AudioItem[];
  handleDropAudio: (item: AudioItem) => void;
  handleRemoveAudio: (id: string) => void;
  showBgmDialog: boolean;
  setShowBgmDialog: (open: boolean) => void;
  showSoundEffectsDialog: boolean;
  setShowSoundEffectsDialog: (open: boolean) => void;
  BgmDialog: React.ReactNode;
  SoundEffectsDialog: React.ReactNode;
  handleRenderFinalVideo: () => void;
  isRendering: boolean;
  selectedBGM: any;
}

export default function TimelineEditorCard({
  timelineItems,
  setTimelineItems,
  imageInputRef,
  handleDrop,
  handleDragOver,
  audioItems,
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
          <div className="flex gap-2 mb-4">
            {/* Add Image Box */}
            <div
              className="w-16 h-16 border-2 border-dashed border-muted-foreground/40 rounded-lg flex items-center justify-center cursor-pointer hover:border-primary/60 transition-colors bg-muted/30"
              onClick={() => imageInputRef.current?.click()}
              title="Add Image"
            >
              <Plus className="w-6 h-6 text-muted-foreground" />
              <input
                ref={imageInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={async e => {
                  const file = e.target.files?.[0];
                  if (file) {
                    setImageUploading(true);
                    setImageUploadError(null);
                    const formData = new FormData();
                    formData.append('file', file);
                    try {
                      const res = await fetch('http://localhost:8000/api/upload-image', {
                        method: 'POST',
                        body: formData,
                      });
                      if (!res.ok) throw new Error('Upload failed');
                      const data = await res.json();
                      const url = data.url;
                      setTimelineItems((prev: any[]) => [
                        ...prev,
                        {
                          type: 'image',
                          url,
                          name: file.name || 'Image',
                          duration: '3',
                          timelineId: Date.now(),
                          id: Date.now(),
                        }
                      ]);
                    } catch (err) {
                      setImageUploadError('Image upload failed. Please try again.');
                      console.error(err);
                    } finally {
                      setImageUploading(false);
                    }
                  }
                }}
                disabled={imageUploading}
              />
            </div>
            {/* Add Text Button */}
            <Button
              variant="outline"
              size="sm"
              className="h-16 flex items-center justify-center px-4"
              onClick={() => setTimelineItems((prev: any[]) => [
                ...prev,
                {
                  type: 'text',
                  text: 'New Text',
                  name: 'Text',
                  duration: '3',
                  timelineId: Date.now(),
                  id: Date.now(),
                }
              ])}
            >
              <span className="flex flex-col items-center">
                <Plus className="w-5 h-5 mb-1" />
                <span className="text-xs">Add Text</span>
              </span>
            </Button>
          </div>
          <div
            className="min-h-[120px] border-2 border-dashed border-muted-foreground/25 rounded-lg p-4 transition-colors hover:border-muted-foreground/50 flex gap-2 flex-wrap"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            {timelineItems.length > 0 ? (
              timelineItems.map((item, idx) => {
                if (item.type === 'clip') {
                  return (
                    <div
                      key={item.timelineId}
                      className="flex items-center gap-2 bg-primary/10 border border-primary/20 rounded-md px-3 py-2"
                      draggable
                      onDragStart={e => {
                        e.dataTransfer.setData('timelineIdx', idx.toString());
                      }}
                      onDrop={e => {
                        e.preventDefault();
                        const fromIdx = Number(e.dataTransfer.getData('timelineIdx'));
                        if (fromIdx === idx) return;
                        setTimelineItems((prev: any[]) => {
                          const arr = [...prev];
                          const [moved] = arr.splice(fromIdx, 1);
                          arr.splice(idx, 0, moved);
                          return arr;
                        });
                      }}
                      onDragOver={e => e.preventDefault()}
                    >
                      <Play className="w-4 h-4" />
                      <span className="text-sm font-medium">{item.name}</span>
                      <span className="text-xs text-muted-foreground">({item.duration})</span>
                      <Button size="sm" variant="ghost" onClick={() => setTimelineItems((prev: any[]) => prev.filter((_: any, i: number) => i !== idx))} className="w-6 h-6 p-0"><Trash2 className="w-3 h-3" /></Button>
                    </div>
                  );
                } else if (item.type === 'image') {
                  return (
                    <div
                      key={item.timelineId}
                      className="flex items-center gap-2 bg-blue-100/40 border border-blue-300/40 rounded-md px-2 py-1"
                      draggable
                      onDragStart={e => {
                        e.dataTransfer.setData('timelineIdx', idx.toString());
                      }}
                      onDrop={e => {
                        e.preventDefault();
                        const fromIdx = Number(e.dataTransfer.getData('timelineIdx'));
                        if (fromIdx === idx) return;
                        setTimelineItems((prev: any[]) => {
                          const arr = [...prev];
                          const [moved] = arr.splice(fromIdx, 1);
                          arr.splice(idx, 0, moved);
                          return arr;
                        });
                      }}
                      onDragOver={e => e.preventDefault()}
                    >
                      <img src={item.url} alt={item.name} className="w-10 h-10 object-cover rounded" />
                      <span className="text-xs text-muted-foreground">{item.name}</span>
                      <Button size="sm" variant="ghost" onClick={() => setTimelineItems((prev: any[]) => prev.filter((_: any, i: number) => i !== idx))} className="w-5 h-5 p-0"><Trash2 className="w-3 h-3" /></Button>
                    </div>
                  );
                } else if (item.type === 'text') {
                  return (
                    <div
                      key={item.timelineId}
                      className="flex items-center gap-2 bg-green-100/40 border border-green-300/40 rounded-md px-2 py-1"
                      draggable
                      onDragStart={e => {
                        e.dataTransfer.setData('timelineIdx', idx.toString());
                      }}
                      onDrop={e => {
                        e.preventDefault();
                        const fromIdx = Number(e.dataTransfer.getData('timelineIdx'));
                        if (fromIdx === idx) return;
                        setTimelineItems((prev: any[]) => {
                          const arr = [...prev];
                          const [moved] = arr.splice(fromIdx, 1);
                          arr.splice(idx, 0, moved);
                          return arr;
                        });
                      }}
                      onDragOver={e => e.preventDefault()}
                    >
                      <input
                        type="text"
                        value={item.text}
                        onChange={e => setTimelineItems((prev: any[]) => prev.map((t: any, i: number) => i === idx ? { ...t, text: e.target.value } : t))}
                        className="text-xs bg-transparent border-none outline-none w-24"
                      />
                      <Button size="sm" variant="ghost" onClick={() => setTimelineItems((prev: any[]) => prev.filter((_: any, i: number) => i !== idx))} className="w-5 h-5 p-0"><Trash2 className="w-3 h-3" /></Button>
                    </div>
                  );
                }
                return null;
              })
            ) : (
              <div className="text-center text-muted-foreground w-full">
                <Move className="w-8 h-8 mx-auto mb-3 opacity-50" />
                <p className="text-sm font-medium mb-1">Drag clips, images, or text here to arrange them</p>
                <p className="text-xs">Create your final video by arranging items in the timeline</p>
              </div>
            )}
          </div>
        </div>

        {/* Audio Track UI inside the Timeline Editor card */}
        <AudioTrack audioItems={audioItems} onDropAudio={handleDropAudio} onRemoveAudio={handleRemoveAudio} />

        {/* Render Button */}
        {(timelineItems.length > 0 || selectedBGM) && (
          <div className="flex justify-end pt-2">
            <Button 
              onClick={handleRenderFinalVideo}
              disabled={isRendering || timelineItems.length === 0}
              className="bg-gradient-to-r from-green-500 to-emerald-500 text-white border-0 hover:from-green-600 hover:to-emerald-600"
            >
              {isRendering ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Rendering...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4 mr-2" />
                  Render Final Video
                </>
              )}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 