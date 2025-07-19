import React from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Wand2, Play } from "lucide-react";

interface GeneratedClipsCardProps {
  generatedClips: any[];
  isGenerating: boolean;
  handleDragStart: (e: React.DragEvent, clip: any) => void;
  handleClipClick: (clip: any) => void;
  UiverseLoader: React.FC;
  project: any;
}

export default function GeneratedClipsCard({
  generatedClips,
  isGenerating,
  handleDragStart,
  handleClipClick,
  UiverseLoader,
  project,
}: GeneratedClipsCardProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Wand2 className="w-5 h-5" />
          Generated Clips
          {generatedClips.length > 0 && (
            <Badge variant="secondary">{generatedClips.length}</Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {isGenerating ? (
          <div className="flex flex-col items-center justify-center py-8">
            <UiverseLoader />
            <p className="text-sm text-muted-foreground mt-4">Analyzing video and generating clips for {project.name}...</p>
          </div>
        ) : generatedClips.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {generatedClips.map((clip) => (
              <div
                key={clip.id}
                draggable
                onDragStart={(e) => handleDragStart(e, clip)}
                onClick={() => handleClipClick(clip)}
                className="group cursor-pointer hover:cursor-grab active:cursor-grabbing border rounded-lg p-2 hover:shadow-md transition-all bg-background hover:border-primary/50"
                aria-grabbed="false"
                onDragEnd={e => e.currentTarget.classList.remove('ring-2', 'ring-primary')}
                onDragEnter={e => e.currentTarget.classList.add('ring-2', 'ring-primary')}
                onDragLeave={e => e.currentTarget.classList.remove('ring-2', 'ring-primary')}
              >
                <div className="aspect-video bg-gradient-to-br from-blue-500 to-purple-600 rounded-md flex items-center justify-center mb-2 relative overflow-hidden">
                  {clip.thumbnail_url ? (
                    <>
                      <img 
                        src={clip.thumbnail_url.startsWith('/') ? `http://localhost:8000${clip.thumbnail_url}` : clip.thumbnail_url}
                        alt={clip.name}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          console.error('Thumbnail load error:', clip.thumbnail_url);
                          e.currentTarget.style.display = 'none';
                        }}
                        onLoad={() => console.log('Thumbnail loaded:', clip.thumbnail_url)}
                      />
                      <div className="absolute inset-0 bg-black/20 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                        <Play className="w-8 h-8 text-white drop-shadow-lg" />
                      </div>
                    </>
                  ) : (
                    <Play className="w-6 h-6 text-white" />
                  )}
                </div>
                <div className="space-y-1">
                  <h4 className="font-medium text-sm">{clip.name}</h4>
                  <p className="text-xs text-muted-foreground">{clip.duration}</p>
                  <p className="text-xs text-muted-foreground">{clip.startTime} - {clip.endTime}</p>
                  <div className="flex items-center gap-1">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-xs">{Math.round(clip.confidence * 100)}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <Wand2 className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">No clips generated yet</p>
            <p className="text-sm">Click "Generate Clips" to create highlight clips from your {project.name} video</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 