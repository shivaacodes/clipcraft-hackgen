import React from "react";
import { Button } from "@/components/ui/button";
import { UploadCloud } from "lucide-react";

interface RenderedVideoPreviewProps {
  renderedVideoUrl: string | null;
  projectId: string;
  onExport: () => void;
}

export default function RenderedVideoPreview({ renderedVideoUrl, projectId, onExport }: RenderedVideoPreviewProps) {
  if (!renderedVideoUrl) return null;
  return (
    <div className="mt-8 flex flex-col items-center gap-4 mb-16">
      <div className="w-full max-w-2xl">
        <h3 className="font-semibold text-lg mb-2">Rendered Video Preview</h3>
        <video
          src={renderedVideoUrl}
          controls
          className="w-full rounded-lg border"
          style={{ maxHeight: '500px' }}
        >
          Your browser does not support the video tag.
        </video>
      </div>
      <Button onClick={onExport}>
        <UploadCloud className="w-4 h-4 mr-2" />
        Export
      </Button>
    </div>
  );
} 