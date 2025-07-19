"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Camera, UploadCloud, Video } from "lucide-react";

export default function FindByImagePage() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [previewImageUrl, setPreviewImageUrl] = useState<string | null>(null);
  const [selectedVideo, setSelectedVideo] = useState<File | null>(null);
  const [previewVideoUrl, setPreviewVideoUrl] = useState<string | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      setPreviewImageUrl(URL.createObjectURL(file));
      // Do not clear video selection
    }
  };

  const handleVideoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedVideo(file);
      setPreviewVideoUrl(URL.createObjectURL(file));
      // Do not clear image selection
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedImage) {
      alert("Finding clips using image! (Feature coming soon)");
      // TODO: Implement API call to find clips by image
    } else if (selectedVideo) {
      alert("Finding clips using video! (Feature coming soon)");
      // TODO: Implement API call to find clips by video
    } else {
      alert("Please select an image or a video to find clips.");
    }
  };

  return (
    <>
      <div className="flex flex-col items-center w-full p-6 py-12 mt-12 min-h-screen pb-20">
        <Camera className="w-12 h-12 text-primary mb-4" />
        <h1 className="text-4xl font-extrabold text-center mb-3 leading-tight">
          Picture This! 📸 Find Your Perfect Clip
        </h1>
        <p className="text-muted-foreground text-center text-lg mb-8">
          Upload your raw video footage and an image. Our AI, powered by OpenCV, intelligently analyzes your content to automatically pinpoint and extract relevant clips that match your image.
        </p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-8 items-center w-full">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">
            {/* Video Upload Option */}
            <label className="flex flex-col items-center gap-4 cursor-pointer p-8 border-2 border-dashed border-primary/50 hover:border-primary transition-all duration-300 bg-gradient-to-br from-background/50 to-background/80 shadow-inner w-full min-w-[320px]">
              <span className="text-xl font-semibold text-primary">Upload your video footage! 🎥</span>
              <input
                type="file"
                accept="video/*"
                onChange={handleVideoChange}
                className="hidden"
              />
              <div className="w-full h-72 bg-muted border-4 border-primary/30 flex items-center justify-center overflow-hidden shadow-lg">
                {previewVideoUrl ? (
                  <video src={previewVideoUrl} controls className="object-cover w-full h-full" />
                ) : (
                  <div className="flex flex-col items-center text-muted-foreground">
                    <Video className="w-16 h-16 mb-2" />
                    <span className="text-lg font-medium">Upload Video</span>
                  </div>
                )}
              </div>
              {selectedVideo && (
                <p className="text-sm text-muted-foreground mt-2">Selected: {selectedVideo.name} 🎉</p>
              )}
            </label>

            {/* Image Upload Option */}
            <label className="flex flex-col items-center gap-4 cursor-pointer p-8 border-2 border-dashed border-primary/50 hover:border-primary transition-all duration-300 bg-gradient-to-br from-background/50 to-background/80 shadow-inner w-full min-w-[320px]">
              <span className="text-xl font-semibold text-primary">Upload your reference image! 🖼️</span>
              <input
                type="file"
                accept="image/*"
                onChange={handleImageChange}
                className="hidden"
              />
              <div className="w-full h-72 bg-muted border-4 border-primary/30 flex items-center justify-center overflow-hidden shadow-lg">
                {previewImageUrl ? (
                  <img src={previewImageUrl} alt="Preview" className="object-cover w-full h-full" />
                ) : (
                  <div className="flex flex-col items-center text-muted-foreground">
                    <UploadCloud className="w-16 h-16 mb-2" />
                    <span className="text-lg font-medium">Upload Image</span>
                  </div>
                )}
              </div>
              {selectedImage && (
                <p className="text-sm text-muted-foreground mt-2">Selected: {selectedImage.name} 🎉</p>
              )}
            </label>
          </div>

          <Button type="submit" disabled={!selectedImage || !selectedVideo} className="w-full text-lg py-3 font-bold shadow-lg hover:shadow-xl transition-all duration-300 mb-12">
            Find My Clips! 🎉
          </Button>
        </form>

        {/* Dummy Placeholder for results */}
        {(selectedImage || selectedVideo) && (
          <div className="mt-12 w-full">
            <h2 className="text-3xl font-bold text-center mb-8 text-primary">Potential Matches Found! ✨</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="flex flex-col items-center gap-4 p-6 bg-card border border-muted-foreground/10 shadow-lg">
                  <div className="w-full h-40 bg-muted flex items-center justify-center overflow-hidden">
                    <span className="text-muted-foreground text-5xl">🎞️</span>
                  </div>
                  <h3 className="text-xl font-semibold text-center">Clip Title {i}</h3>
                  <p className="text-sm text-muted-foreground text-center">A short description of what this clip might contain, based on your image.</p>
                  <Button variant="outline" className="w-full">View Clip</Button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </>
}
