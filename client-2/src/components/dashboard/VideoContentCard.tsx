import React from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Scissors, Upload, Wand2 } from "lucide-react";

interface VideoContentCardProps {
  selectedVideo: File | null;
  videoUrl: string | null;
  handleRemoveVideo: () => void;
  showStatusIndicator: boolean;
  statusState: string;
  currentStepIdx: number;
  statusSteps: { key: string; label: string; icon: any; color: string }[];
  project: any;
  isGenerating: boolean;
  handleGenerateClips: () => void;
  fastMode: boolean;
  setFastMode: (v: boolean) => void;
  handleTestClips: () => void;
  isImporting: boolean; // <-- add this
}

// Loader component (Uiverse.io by david-mohseni) - small version
function UiverseLoader({ small = false }: { small?: boolean }) {
  return (
    <div className={`loader mx-auto my-8 ${small ? 'loader-small' : ''}`.trim()}>
      <div className="bar1"></div>
      <div className="bar2"></div>
      <div className="bar3"></div>
      <div className="bar4"></div>
      <div className="bar5"></div>
      <div className="bar6"></div>
      <div className="bar7"></div>
      <div className="bar8"></div>
      <div className="bar9"></div>
      <div className="bar10"></div>
      <div className="bar11"></div>
      <div className="bar12"></div>
    </div>
  );
}

export default function VideoContentCard({
  selectedVideo,
  videoUrl,
  handleRemoveVideo,
  showStatusIndicator,
  statusState,
  currentStepIdx,
  statusSteps,
  project,
  isGenerating,
  handleGenerateClips,
  fastMode,
  setFastMode,
  handleTestClips,
  isImporting, // <-- add this
}: VideoContentCardProps) {
  return (
    <div className="mt-4 border rounded-lg p-6 bg-muted/20">
      {isImporting ? (
        <div className="flex flex-col items-center justify-center min-h-[300px]">
          <UiverseLoader />
          <div className="mt-4 text-lg font-medium text-muted-foreground">Importing video...</div>
        </div>
      ) : selectedVideo && videoUrl ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-lg">Imported Video</h3>
              <p className="text-sm text-muted-foreground">
                {selectedVideo.name} ({(selectedVideo.size / (1024 * 1024)).toFixed(2)} MB)
              </p>
            </div>
            <Button variant="destructive" size="sm" onClick={handleRemoveVideo}>
              Remove
            </Button>
          </div>

          <div className="flex w-full gap-6 items-center">
            <div className="flex-1 relative">
              <video
                src={videoUrl}
                controls
                className="w-full max-w-2xl h-auto rounded-lg border"
                style={{ maxHeight: '500px' }}
              >
                Your browser does not support the video tag.
              </video>
            </div>
            {showStatusIndicator && ["queued", "transcribing", "analyzing", "finalizing"].includes(statusState) && (
              <div className="flex flex-col items-center justify-center h-full min-w-[180px] select-none animate-pulse mt-16 ml-[-96px]">
                <div
                  className="flex flex-col items-center transition-transform duration-500"
                  style={{ transform: `translateY(-${currentStepIdx * 80}px)` }}
                >
                  {statusSteps.map((step, idx) => {
                    const isCurrent = idx === currentStepIdx;
                    const isPrevOrNext = Math.abs(idx - currentStepIdx) === 1;
                    return (
                      <div
                        key={step.key}
                        className={`flex flex-row items-center justify-center mb-6 transition-all duration-500 gap-4 ${
                          isCurrent
                            ? "opacity-100 scale-110"
                            : isPrevOrNext
                            ? "opacity-40 scale-90"
                            : "opacity-0 scale-75 pointer-events-none"
                        }`}
                        style={{ minHeight: 80 }}
                      >
                        <step.icon className={`w-8 h-8 md:w-10 md:h-10 lg:w-12 lg:h-12 xl:w-[2.25rem] xl:h-[2.25rem] ${step.color}`} />
                        <span className={`text-2xl font-bold tracking-wide ${step.color}`}>{step.label}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          <div className="flex gap-2 flex-wrap">
            <Button 
              onClick={handleGenerateClips}
              disabled={isGenerating}
              className="bg-gradient-to-r from-purple-500 to-pink-500 text-white border-0 hover:from-purple-600 hover:to-pink-600"
              size="sm"
            >
              <Wand2 className="w-4 h-4 mr-2" />
              {isGenerating ? "Generating..." : "Generate Clips"}
            </Button>
            <div className="flex items-center gap-2">
              <label htmlFor="fast-mode" className="text-sm font-medium">
                ⚡ Fast Mode
              </label>
              <input
                id="fast-mode"
                type="checkbox"
                checked={fastMode}
                onChange={e => setFastMode(e.target.checked)}
                className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
              />
              <span className="text-xs text-muted-foreground">
                {fastMode ? "Fast generation" : "High quality"}
              </span>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center text-muted-foreground">
          <Upload className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p className="text-lg font-medium mb-2">No video imported yet</p>
          <p className="text-sm">Click "Import Video" to select a video file for your {project.name} project</p>
          <p className="text-xs mt-2">Supported formats: MP4, MOV, AVI, MKV, WebM (Max 100MB)</p>
        </div>
      )}
    </div>
  );
} 