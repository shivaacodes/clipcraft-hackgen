import React from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Play, Download, Plus } from "lucide-react";

interface ClipPlayerDialogProps {
  showClipPlayer: boolean;
  setShowClipPlayer: (open: boolean) => void;
  selectedClip: any;
  setTimelineItems: React.Dispatch<React.SetStateAction<any[]>>;
}

export default function ClipPlayerDialog({
  showClipPlayer,
  setShowClipPlayer,
  selectedClip,
  setTimelineItems,
}: ClipPlayerDialogProps) {
  return (
    <Dialog open={showClipPlayer} onOpenChange={setShowClipPlayer}>
      <DialogContent className="max-w-4xl w-full">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Play className="w-5 h-5" />
            {selectedClip?.name || 'Clip Player'}
          </DialogTitle>
        </DialogHeader>
        {selectedClip && (
          <div className="space-y-4">
            {/* Video Player */}
            <div className="relative">
              {selectedClip.clip_url ? (
                <video
                  src={`http://localhost:8000${selectedClip.clip_url}`}
                  controls
                  autoPlay
                  className="w-full max-h-[60vh] rounded-lg bg-black"
                  poster={selectedClip.thumbnail_url ? `http://localhost:8000${selectedClip.thumbnail_url}` : undefined}
                  onError={(e) => console.error('Video playback error:', e)}
                  onLoadStart={() => console.log('Video loading started:', selectedClip.clip_url)}
                  onCanPlay={() => console.log('Video can play')}
                >
                  Your browser does not support the video tag.
                </video>
              ) : (
                <div className="w-full h-60 bg-gray-200 dark:bg-gray-800 rounded-lg flex items-center justify-center">
                  <p className="text-gray-500">No video available</p>
                </div>
              )}
            </div>
            {/* Clip Info */}
            <div className="grid grid-cols-2 gap-4 p-4 bg-muted/20 rounded-lg">
              <div>
                <h4 className="font-semibold mb-2">Clip Details</h4>
                <div className="space-y-1 text-sm">
                  <p><span className="text-muted-foreground">Duration:</span> {selectedClip.duration}</p>
                  <p><span className="text-muted-foreground">Time Range:</span> {selectedClip.startTime} - {selectedClip.endTime}</p>
                  <p><span className="text-muted-foreground">Confidence:</span> {Math.round(selectedClip.confidence * 100)}%</p>
                  <p><span className="text-muted-foreground">Vibe:</span> {selectedClip.vibe || 'N/A'}</p>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-2">AI Analysis</h4>
                <div className="space-y-1 text-sm">
                  {selectedClip.scores && (
                    <>
                      <p><span className="text-muted-foreground">Vibe Match:</span> {selectedClip.scores.vibe_match || 0}/100</p>
                      <p><span className="text-muted-foreground">Age Match:</span> {selectedClip.scores.age_group_match || 0}/100</p>
                      <p><span className="text-muted-foreground">Clip Potential:</span> {selectedClip.scores.clip_potential || 0}/100</p>
                    </>
                  )}
                  <p className="text-xs text-muted-foreground mt-2">{selectedClip.reason}</p>
                </div>
              </div>
            </div>
            {/* Action Buttons */}
            <div className="flex gap-2 justify-end sticky bottom-0 bg-background py-4 z-10 border-t mt-4">
              <Button variant="outline" size="sm">
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  setTimelineItems((prev: any[]) => [...prev, { ...selectedClip, type: 'clip', timelineId: Date.now() }]);
                  setShowClipPlayer(false);
                }}
              >
                <Plus className="w-4 h-4 mr-2" />
                Add to Timeline
              </Button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
} 