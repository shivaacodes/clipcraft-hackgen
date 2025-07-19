"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { UploadCloud } from "lucide-react";
import { exportPlatforms } from "../page";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";

export default function ExportPage() {
  const params = useParams();
  const router = useRouter();
  const [isExporting, setIsExporting] = useState(false);
  const [previewIdx, setPreviewIdx] = useState<number|null>(null);
  const placeholderImg = "https://via.placeholder.com/480x270?text=Final+Render";

  // You may want to fetch project/rendered video info here if needed

  const handleExport = (platformId: string, idx: number) => {
    window.location.href = "https://studio.youtube.com/channel/UCmZSdp3gCi7FumEwgSMrjag/videos/upload?d=ud&filter=%5B%5D&sort=%7B%22columnType%22%3A%22date%22%2C%22sortOrder%22%3A%22DESCENDING%22%7D";
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-background py-12 px-4">
      <div className="w-full px-8 mx-auto">
        <h1 className="text-3xl font-bold mb-2 text-center">Export Video</h1>
        <p className="text-muted-foreground text-center mb-8">Choose your platform and export format</p>
        <div className="border-b border-muted mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-y-[6rem] gap-x-[6rem] justify-items-center w-full px-8">
          {exportPlatforms.map((platform, idx) => {
            const IconComponent = platform.icon;
            // Demo durations for each card
            const demoDurations = ['10 sec', '15 sec', '20 sec'];
            return (
              <div
                key={platform.id}
                className="border rounded-xl p-8 my-4 shadow-lg hover:shadow-2xl transition-all cursor-pointer group hover:border-primary/50 min-h-[340px] min-w-[320px] flex flex-col bg-background/80"
                onClick={() => !isExporting && handleExport(platform.id, idx)}
              >
                {/* Demo duration text */}
                <div className="text-center mb-2 text-lg font-bold text-primary">
                  {demoDurations[idx]}
                </div>
                <div className="text-center space-y-6 flex-1 flex flex-col justify-between">
                  <div className="flex flex-col items-center gap-4">
                    <div className="flex justify-center">
                      <IconComponent
                        className="w-14 h-14"
                        style={{ color: platform.iconColor }}
                      />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg mb-2">{platform.name}</h3>
                      <p className="text-sm text-muted-foreground leading-relaxed">{platform.description}</p>
                    </div>
                  </div>
                  <div className="bg-muted/40 p-4 rounded-lg text-sm mt-4">
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Format:</span>
                        <span className="font-semibold">{platform.format}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Dimensions:</span>
                        <span className="font-semibold">{platform.dimensions}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Aspect Ratio:</span>
                        <span className="font-semibold">{platform.aspectRatio}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-muted-foreground">Max Duration:</span>
                        <span className="font-semibold">{platform.duration}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <Button
                  className="w-full mt-6 h-10 text-sm"
                  disabled={isExporting}
                  onClick={e => {
                    e.stopPropagation();
                    handleExport(platform.id, idx);
                  }}
                >
                  {isExporting ? (
                    <div className="flex items-center gap-2">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Exporting...
                    </div>
                  ) : (
                    <>
                      <UploadCloud className="w-4 h-4 mr-2" />
                      Export for {platform.name}
                    </>
                  )}
                </Button>
                {/* Download button below Export button */}
                <a href={placeholderImg} download={`final-${platform.id}.png`} className="w-full block mt-3">
                  <Button variant="secondary" className="w-full h-10 text-sm">Download</Button>
                </a>
              </div>
            );
          })}
        </div>
        {/* Modal preview removed as per request */}
      </div>
    </div>
  );
} 